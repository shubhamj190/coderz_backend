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

class AdminHomeView(APIView):
    permission_classes = [IsSpecificAdmin]  # Only authenticated users can access this view

    def get(self, request):
        return Response({"message": "Welcome to the Admin home page!"}, status=status.HTTP_200_OK)


class TeacherHomeView(APIView):
    permission_classes = [IsSpecificTeacher]  # Only authenticated users can access this view

    def get(self, request):
        return Response({"message": "Welcome to the Teacher home page!"}, status=status.HTTP_200_OK)
    
class StudentHomeView(APIView):
    permission_classes = [IsSpecificStudent]  # Only authenticated users can access this view

    def get(self, request):
        return Response({"message": "Welcome to the Student home page!"}, status=status.HTTP_200_OK)