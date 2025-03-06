# apps/accounts/api/v1/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.projects.api.v1.serializers import ClassroomProjectSerializer, ProjectSessionSerializer, ProjectSubmissionSerializer
from apps.projects.models.projects import ClassroomProject, ProjectSession
from core.permissions.role_based import IsAdminOrTeacher, IsSpecificStudent
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
    
class UpdateProjectSessionView(APIView):
    """
    API to update a Project Session. 
    Only Admins and Teachers can update sessions.
    """
    permission_classes = [IsAdminOrTeacher]
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads

    def put(self, request, session_id, *args, **kwargs):
        """
        Full update (PUT) - All fields must be provided.
        """
        session = get_object_or_404(ProjectSession, id=session_id)  # Ensure session exists
        serializer = ProjectSessionSerializer(session, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, session_id, *args, **kwargs):
        """
        Partial update (PATCH) - Only provided fields are updated.
        """
        session = get_object_or_404(ProjectSession, id=session_id)
        serializer = ProjectSessionSerializer(session, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProjectSessionListView(APIView):
    """
    API to get all project sessions or filter by project ID.
    Only Admins and Teachers can access.
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, *args, **kwargs):
        """
        Fetch all project sessions or sessions of a specific project.
        Example:
        - GET /api/project-sessions/ → Get all sessions.
        - GET /api/project-sessions/?project_id=3 → Get sessions for project ID 3.
        """
        project_id = request.GET.get('project_id')  # Fetch project_id from query params
        sessions = ProjectSession.objects.all()

        if project_id:
            sessions = sessions.filter(project_id=project_id)

        serializer = ProjectSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectSubmissionCreateView(APIView):
    """
    API for students to submit project files.
    Only authenticated students can submit.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsSpecificStudent]

    def post(self, request, *args, **kwargs):
        """
        Handle project submission.
        """
        student = request.user  # Get logged-in student

        # Ensure student role is valid
        if not hasattr(student, 'role') or student.role != 'Learner':
            return Response(
                {"error": "Only students can submit projects."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate project exists
        project_id = request.data.get("project")
        try:
            project = ClassroomProject.objects.get(id=project_id)
        except ClassroomProject.DoesNotExist:
            return Response(
                {"error": "Project not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Create submission
        data = {
            "project": project.id,
            "student": student.id,
            "submission_file": request.FILES.get("submission_file"),
        }
        serializer = ProjectSubmissionSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Project submitted successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)