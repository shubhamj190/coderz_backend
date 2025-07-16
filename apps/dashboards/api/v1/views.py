import base64
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models.user import UserDetails, UsersIdentity
from apps.projects.models.projects import ClassroomProject, ProjectSubmission
from core.permissions.role_based import IsSpecificAdmin, IsSpecificTeacher, IsSpecificStudent
from django.db.models import Q


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

        


        return Response({
            "total_projects_assigned": total_projects_assigned,
            "total_projects_uploaded": total_projects_uploaded,
            "total_projects_reviewed": total_projects_reviewed
        })

    def get_default_dashboard(self):
        return Response({
            "message": "Welcome!",
            "available_views": ["Home", "Profile", "Support"]
        }, status=status.HTTP_200_OK)