import base64
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models.user import GroupMaster, TeacherLocationDetails, UserDetails, UserGroup, UserSessionLog, UsersIdentity
from apps.projects.models.projects import ClassroomProject, ProjectSubmission
from core.permissions.role_based import IsSpecificAdmin, IsSpecificTeacher, IsSpecificStudent
from django.db.models import Q, Avg


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
            "action": f"/teacher/project-details?group_id={group_id}"
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



        return Response({
            "total_projects_assigned": total_projects_assigned,
            "total_projects_uploaded": total_projects_uploaded,
            "total_projects_reviewed": total_projects_reviewed,
            "group_details": result,
            'average_session_duration_minutes': round((average_duration or 0) / 60, 2)
        })
    


    def get_default_dashboard(self):
        return Response({
            "message": "Welcome!",
            "available_views": ["Home", "Profile", "Support"]
        }, status=status.HTTP_200_OK)