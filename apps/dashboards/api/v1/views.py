import base64
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from core.permissions.role_based import IsSpecificAdmin, IsSpecificTeacher, IsSpecificStudent


logger = logging.getLogger(__name__)

class HomeView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the logged-in user
        user_type = user.details.UserType  # Retrieve UserType if it exists

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
        return Response({
            "message": "Welcome to the Teacher Portal!",
            "available_views": ["My Classes", "Assessments", "Student Progress"]
        }, status=status.HTTP_200_OK)

    def get_default_dashboard(self):
        return Response({
            "message": "Welcome!",
            "available_views": ["Home", "Profile", "Support"]
        }, status=status.HTTP_200_OK)