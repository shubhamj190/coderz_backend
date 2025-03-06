# apps/accounts/api/v1/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.projects.api.v1.serializers import ClassroomProjectSerializer, ProjectSessionSerializer
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
    
class CreateProjectSessionView(APIView):
    """
    API to create a Project Session. 
    Only Admins and Teachers can create sessions.
    """
    permission_classes = [IsAdminOrTeacher]  
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads

    def post(self, request, *args, **kwargs):
        serializer = ProjectSessionSerializer(data=request.data)

        if serializer.is_valid():
            project_id = request.data.get("project")
            project = get_object_or_404(ClassroomProject, id=project_id)  # Validate project
            
            serializer.save(project=project)  # Save with the validated project
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)