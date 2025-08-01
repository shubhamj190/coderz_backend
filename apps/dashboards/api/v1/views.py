import base64
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models.user import GroupMaster, MissionActivitySummary, TeacherLocationDetails, UserDetails, UserGroup, UserSessionLog, UsersIdentity
from apps.projects.models.projects import ClassroomProject, ProjectSubmission
from core.permissions.role_based import IsSpecificAdmin, IsSpecificTeacher, IsSpecificStudent
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

logger = logging.getLogger(__name__)

class HomeView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the logged-in user
        user_identity = UsersIdentity.objects.filter(UserName=user.username).first()
        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        user_type = user_details.UserType

        if not user_type:
            return Response({"error": "User type not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Map user types to their respective functions
        user_type_functions = {
            "Admin": self.get_admin_dashboard,
            "Learner": self.get_learner_dashboard,
            "Teacher": self.get_teacher_dashboard,
        }

        # Get the appropriate function or use the default
        view_function = user_type_functions.get(user_type, self.get_default_dashboard)
        return view_function()

    def get_admin_dashboard(self):
        return Response({
            "message": "Welcome to the Admin Dashboard!",
            "available_views": ["Manage Users", "Reports", "Settings"]
        }, status=status.HTTP_200_OK)

    def get_learner_dashboard(self):
        return Response({
            "message": "Welcome to the Student Portal!",
            "available_views": ["My Courses", "Assignments", "Grades"]
        }, status=status.HTTP_200_OK)

    def get_teacher_dashboard(self):
        
        teacher = self.request.user  # Assuming `request.user` is a Teacher
        teacher_identity=UsersIdentity.objects.filter(UserName=teacher.username).first()
        if teacher_identity is not None:
            teacher=teacher_identity
        teacher_id = teacher.UserId
        # Total Projects Assigned
        total_projects_assigned = ClassroomProject.objects.filter(assigned_teacher=teacher).count()

        # Total Projects Uploaded (has a file)
        total_projects_uploaded = ProjectSubmission.objects.filter(project__assigned_teacher = teacher).exclude(
            submission_file__isnull=True
        ).exclude(
            submission_file=''
        ).count()

        # Total Projects Reviewed (has feedback or evaluation)
        total_projects_reviewed = ProjectSubmission.objects.filter(project__assigned_teacher = teacher)\
        .filter(teacher_evaluation__isnull=False).count()

        group_mappings = TeacherLocationDetails.objects.filter(
        UserId=teacher_id,
        IsDeleted=False
        )
        result = []
        for mapping in group_mappings:
            group_id = mapping.GroupId
            location_id = mapping.LocationId
            # Get students in this group
            student_qs = UserGroup.objects.filter(
                GroupId=group_id,
                LocationId=location_id,
                IsDeleted=False
            ).values_list('user__UserId', flat=True)

            total_students = student_qs.count()

            # Number of project submissions from this group
            submitted_count = ProjectSubmission.objects.filter(
                student_id__in=student_qs
            ).count()

            # You may fetch grade from GroupMaster or construct manually
            group_name = GroupMaster.objects.filter(
                GroupId=group_id
            ).first().GroupName if GroupMaster.objects.filter(GroupId=group_id).exists() else f"Group {group_id}"

            result.append({
            "grade": group_name,
            "total_students": total_students,
            "projects_assigned": total_students,  # assuming assigned = total
            "projects_submitted": submitted_count,
            "group_id": GroupMaster.objects.get(GroupId=group_id).GroupId,
        })
            
        teacher_groups = group_mappings.values_list('GroupId', flat=True).distinct()

        student_user_ids = UserGroup.objects.filter(
            GroupId__in=teacher_groups,
            IsDeleted=False
        ).values_list('user_id', flat=True)

        average_duration = UserSessionLog.objects.filter(
            UserId__in=student_user_ids,
            session_duration__isnull=False
        ).aggregate(avg_duration=Avg('session_duration'))['avg_duration']

        pdf_count = MissionActivitySummary.objects.filter(
            user_id__in=student_user_ids,
            content_type_code__in=['04','4', '05', '5']  # Assuming these are the codes for PDF notes
        ).count()

        quiz_count = MissionActivitySummary.objects.filter(
            user_id__in=student_user_ids,
            content_type_code__in=['08','8', '09', '9']  # Assuming these are the codes for PDF notes
        ).count()

        return Response({
            "total_projects_assigned": total_projects_assigned,
            "total_projects_uploaded": total_projects_uploaded,
            "total_projects_reviewed": total_projects_reviewed,
            "group_details": result,
            'average_session_duration_minutes': round((average_duration or 0) / 60, 2),
            "pdf_notes_accessed": pdf_count,
            "quizzes_attempted": quiz_count,
        })


    def get_default_dashboard(self):
        return Response({
            "message": "Welcome!",
            "available_views": ["Home", "Profile", "Support"]
        }, status=status.HTTP_200_OK)
    
class GetTeacherStudentsProjectReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        teacher_identity = UsersIdentity.objects.filter(UserName=user.username).first()
        if not teacher_identity:
            return Response({"detail": "Teacher identity not found."}, status=404)

        # Get optional group_id
        group_id = request.GET.get('group_id')
        # Filter projects by teacher and optionally by group
        projects_qs = ClassroomProject.objects.filter(assigned_teacher=teacher_identity)
        if group_id:
            projects_qs = projects_qs.filter(group__GroupId=group_id)

        project_ids = projects_qs.values_list('id', flat=True)
        groups = projects_qs.values_list('group__GroupId', flat=True).distinct()

        # Get students in these groups
        students = UserGroup.objects.filter(GroupId__in=groups)
        data = []

        for student in students:
            assigned_projects_count = projects_qs.filter(group__GroupId=student.GroupId).count()
            submitted_projects_count = ProjectSubmission.objects.filter(
                student=student.user,
                project_id__in=project_ids
            ).count()
            student_details = UserDetails.objects.filter(UserId=student.user.UserId).first()
            if not student_details:
                continue
            data.append({
                "grade": GroupMaster.objects.get(GroupId=student.GroupId).GroupName,
                "student_name": f"{student_details.FirstName} {student_details.LastName}",
                "projects_assigned": assigned_projects_count,
                "projects_submitted": submitted_projects_count,
                "student_id": student.user.UserId,
                "report_url": f"/reports/student/{student.user.UserId}/"
            })

        return Response({"report": data})
    
class StudentDashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request, student_id):
        student = get_object_or_404(UsersIdentity, UserId=student_id)
        user = student
        group = UserGroup.objects.filter(user=user).first()
        if not group:
            return Response({"error": "Student group not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_details = UserDetails.objects.filter(UserId=student.UserId).first()
        if not user_details:
            return Response({"error": "User details not found."}, status=status.HTTP_404_NOT_FOUND)

        # Content type codes
        QUIZ_CODES = ['8', '9']
        PDF_CODES = ['4', '5']
        PRACTICE_CODES = ['6']       # Update if necessary
        PROJECT_CODES = ['7']        # Update if necessary

        # Learn Summary
        learn_summary = {
            "quiz": {
                "viewed": MissionActivitySummary.objects.filter(
                    user_id=student.UserId,
                    content_type_code__in=QUIZ_CODES
                ).count()
            },
            "pdf_count": {
                "viewed": MissionActivitySummary.objects.filter(
                    user_id=student.UserId,
                    content_type_code__in=PDF_CODES
                ).count()
            }
        }

        # Project Summary
        assigned_projects = ClassroomProject.objects.filter(group=group.GID).count()
        uploaded_projects = ProjectSubmission.objects.filter(student=student).count()
        reviewed_projects = ProjectSubmission.objects.filter(
            student=student
        ).exclude(teacher_evaluation=None).count()

        project_summary = {
            "assigned": assigned_projects,
            "uploaded": uploaded_projects,
            "reviewed": reviewed_projects
        }

        # Time Spent
        total_session = UserSessionLog.objects.filter(UserId=user)
        total_spent = total_session.aggregate(total=Sum('session_duration'))['total'] or 0
        allotted_time = assigned_projects * 2

        total_time = {
            "allotted_time": allotted_time,
            "spent_time": round(total_spent / 60, 2)
        }

        # Daily Activity (from MissionActivitySummary)
        import pdb; pdb.set_trace()
        daily_activity_data = MissionActivitySummary.objects.filter(
            user_id=student.UserId
        ).annotate(date=TruncDate('modified_on')).values('date').annotate(
            quiz_attempted=Count('mission_activity_summary_id', filter=Q(content_type_code__in=QUIZ_CODES)),
            practice_papers_downloaded=Count('mission_activity_summary_id', filter=Q(content_type_code__in=PRACTICE_CODES)),
            notes_viewed=Count('mission_activity_summary_id', filter=Q(content_type_code__in=PDF_CODES)),
            projects_completed=Count('mission_activity_summary_id', filter=Q(content_type_code__in=PROJECT_CODES)),
            session_time=Sum('total_access_duration')
        ).order_by('date')

        daily_activity = []
        for row in daily_activity_data:
            daily_activity.append({
                "date": row['date'],
                "quiz_attempted": row['quiz_attempted'],
                "practice_papers_downloaded": row['practice_papers_downloaded'],
                "notes_viewed": row['notes_viewed'],
                "projects_completed": row['projects_completed'],
                "session_time": round(row['session_time'] or 0, 2)
            })

        return Response({
            "student_name": f"{user_details.FirstName} {user_details.LastName}",
            "grade": group.GID.GroupName,
            "learn_summary": learn_summary,
            "project_summary": project_summary,
            "total_time_spent": total_time,
            "daily_activity": daily_activity
        })