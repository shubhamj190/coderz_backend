# apps/accounts/api/v1/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.projects.api.v1.serializers import ClassroomProjectSerializer
from apps.projects.models.projects import ClassroomProject
from core.permissions.role_based import IsAdminOrTeacher
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class ClassroomProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admin to create, update, delete, and list classroom projects.
    Teacher assignment is automatically handled based on grade and division.
    """
    queryset = ClassroomProject.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ClassroomProjectSerializer
    permission_classes = [IsAdminOrTeacher]  # Replace with [IsSpecificAdmin] if you have that

    def destroy(self, request, *args, **kwargs):
        """
        Optionally, you can override destroy to provide custom deletion logic.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Project deleted successfully."}, status=status.HTTP_204_NO_CONTENT)