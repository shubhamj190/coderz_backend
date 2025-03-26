# apps/accounts/api/v1/views.py
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.projects.api.v1.serializers import ClassroomProjectSerializer, ProjectAssetSerializer, ProjectSessionSerializer, ProjectSubmissionSerializer, ReflectiveQuizSerializer
from apps.projects.models.projects import ClassroomProject, ProjectAsset, ProjectSession, ReflectiveQuiz
from core.permissions.role_based import IsAdminOrTeacher, IsSpecificStudent
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

class ClassroomProjectCreateView(CreateAPIView):
    queryset = ClassroomProject.objects.all()
    serializer_class = ClassroomProjectSerializer
    
class ProjectAssetCreateView(CreateAPIView):
    serializer_class = ProjectAssetSerializer

    def post(self, request, project_id, *args, **kwargs):
        """
        Upload multiple assets for a given ClassroomProject.
        """
        try:
            project = ClassroomProject.objects.get(id=project_id)
        except ClassroomProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        asset_files = request.FILES.getlist('files')  # Get multiple files
        file_types = request.data.getlist('file_types')  # Get corresponding file types

        if len(asset_files) != len(file_types):
            return Response({"error": "Mismatch between files and file types"}, status=status.HTTP_400_BAD_REQUEST)

        assets = []
        for file, file_type in zip(asset_files, file_types):
            asset = ProjectAsset.objects.create(project=project, file=file, file_type=file_type)
            assets.append(ProjectAssetSerializer(asset).data)

        return Response(assets, status=status.HTTP_201_CREATED)
    
class ReflectiveQuizCreateView(CreateAPIView):
    serializer_class = ReflectiveQuizSerializer

    def post(self, request, project_id, *args, **kwargs):
        """
        Create multiple quizzes for a given ClassroomProject.
        """
        try:
            project = ClassroomProject.objects.get(id=project_id)
        except ClassroomProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        quizzes_data = request.data.get('quizzes', [])

        if not quizzes_data:
            return Response({"error": "No quizzes provided"}, status=status.HTTP_400_BAD_REQUEST)

        quizzes = []
        for quiz_data in quizzes_data:
            quiz = ReflectiveQuiz.objects.create(project=project, **quiz_data)
            quizzes.append(ReflectiveQuizSerializer(quiz).data)

        return Response(quizzes, status=status.HTTP_201_CREATED)

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