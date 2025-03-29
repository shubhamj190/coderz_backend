# apps/accounts/api/v1/views.py
import json
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, UpdateAPIView,RetrieveUpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.accounts.models.user import GroupMaster, TeacherLocationDetails, UserDetails, UserGroup
from apps.projects.api.v1.serializers import ClassroomProjectSerializer, ProjectAssetSerializer, ProjectSessionSerializer, ProjectSubmissionSerializer, ReflectiveQuizSerializer, ReflectiveQuizSubmissionSerializer, StudentClassroomProjectSerializer, TeacherClassroomProjectSerializer, UpdateProjectAssetsSerializer
from apps.projects.models.projects import ClassroomProject, ProjectAsset, ProjectSession, ProjectSubmission, ReflectiveQuiz, ReflectiveQuizSubmission
from core.permissions.role_based import IsAdminOrTeacher, IsAdminTeacherStudent, IsSpecificStudent, IsSpecificAdmin, IsSpecificTeacher
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

User = get_user_model()

class ClassroomProjectCreateView(CreateAPIView):
    queryset = ClassroomProject.objects.all()
    serializer_class = ClassroomProjectSerializer
    permission_classes = [IsSpecificAdmin]  # Optional: Require authentication
    
class ClassroomProjectListView(ListAPIView):
    queryset = ClassroomProject.objects.all()
    serializer_class = ClassroomProjectSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["grade", "division"]  # Filters for grade and division
    ordering_fields = ["due_date", "title"]  # Allow ordering by due_date & title
    
class ClassroomProjectRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = ClassroomProject.objects.all()
    serializer_class = ClassroomProjectSerializer
    parser_classes = (MultiPartParser, FormParser)  # Supports file uploads
    permission_classes = [IsSpecificAdmin]  # Optional authentication

    def get_object(self):
        """
        Fetch the ClassroomProject object based on the provided `pk`
        """
        project_id = self.kwargs.get("pk")
        return ClassroomProject.objects.get(id=project_id)

class ProjectAssetCreateView(CreateAPIView):
    serializer_class = ProjectAssetSerializer

    def post(self, request, project_id, *args, **kwargs):
        try:
            project = ClassroomProject.objects.get(id=project_id)
        except ClassroomProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        asset_files = request.FILES.getlist('asset_files')  # Get multiple files
        file_types_raw = request.POST.get('file_types') # Get file types as a list

        # Ensure `file_types_raw` is valid JSON and parse it
        try:
            file_types = json.loads(file_types_raw) if file_types_raw else []
        except json.JSONDecodeError:
            return Response({"error": "Invalid file_types format"}, status=status.HTTP_400_BAD_REQUEST)
        if len(asset_files) != len(file_types):
            return Response({"error": "Mismatch between files and file types"}, status=status.HTTP_400_BAD_REQUEST)

        assets = []
        for file, file_type in zip(asset_files, file_types):
            asset = ProjectAsset.objects.create(
                project=project,
                file=file,
                file_type=file_type.strip()  # Ensure no unwanted characters
            )
            assets.append(ProjectAssetSerializer(asset).data)

        return Response(assets, status=status.HTTP_201_CREATED)
    
class RetrieveUpdateProjectAssetsView(RetrieveUpdateAPIView):
    queryset = ClassroomProject.objects.all()
    serializer_class = UpdateProjectAssetsSerializer
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        """Retrieve all assets for a Classroom Project"""
        project = self.get_object()
        assets = project.assets.all()
        serializer = ProjectAssetSerializer(assets, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update assets for a Classroom Project"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project assets updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
    
class ReflectiveQuizRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a Reflective Quiz instance.
    """
    queryset = ReflectiveQuiz.objects.all()
    serializer_class = ReflectiveQuizSerializer
    lookup_field = "id"  # The field used for retrieving the quiz

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
    permission_classes = [IsAdminTeacherStudent]

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
            "feedback": request.data.get("feedback"),
        }
        serializer = ProjectSubmissionSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Project submitted successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProjectSubmissionListView(APIView):
    permission_classes = [IsAdminTeacherStudent]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_type = user.details.UserType  # Assuming user_type is stored in UserDetails model

        # **Admin: Fetch all submissions**
        if user_type == "Admin":
            submissions = ProjectSubmission.objects.all()

        # **Teacher: Fetch submissions for projects linked to teacher's group**
        elif user_type == "Teacher":
            group_teacher = TeacherLocationDetails.objects.filter(UserId=user.UserId).values_list('GID_id', flat=True)
            projects = ClassroomProject.objects.filter(group__GID__in=[group_teacher])
            submissions = ProjectSubmission.objects.filter(project__in=projects)

        # **Student: Fetch only the logged-in student's submissions**
        elif user_type == "Learner":
            submissions = ProjectSubmission.objects.filter(student=user.details)

        else:
            return Response(
                {"error": "Unauthorized user type."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProjectSubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeacherProjectsView(APIView):
    permission_classes = [IsSpecificTeacher]  # Ensure only logged-in users can access

    def get(self, request, *args, **kwargs):
        teacher = request.user  # Assuming `request.user` is a Teacher

        # Retrieve all projects assigned to the logged-in teacher
        projects = (
            ClassroomProject.objects
            .filter(assigned_teacher=teacher)
            .prefetch_related("assets", "quizzes")
        )

        serializer = TeacherClassroomProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeacherProjectDetailView(APIView):
    permission_classes = [IsSpecificTeacher]

    def get(self, request, project_id, *args, **kwargs):
        teacher = request.user  # Assuming `request.user` is a Teacher

        try:
            # Fetch project assigned to this teacher
            project = (
                ClassroomProject.objects
                .filter(id=project_id, assigned_teacher=teacher)
                .prefetch_related("assets", "quizzes")
                .first()
            )

            # Check if the project exists and is assigned to the teacher
            if not project:
                return Response(
                    {"error": "Project not found or you are not authorized to view it."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize project
            serializer = TeacherClassroomProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ClassroomProject.DoesNotExist:
            return Response(
                {"error": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class StudentProjectsView(APIView):
    permission_classes = [IsSpecificStudent]  # Ensure only authenticated students can access

    def get(self, request, *args, **kwargs):
        student = request.user  # Assuming the student is logged in

        # Ensure the student has groups assigned
        student_groups = UserGroup.objects.filter(user=student).values_list('GroupId', flat=True)
        if not student_groups.exists():
            return Response({"message": "No groups assigned to this student."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch projects associated with the student's groups
        projects = (
            ClassroomProject.objects
            .filter(group__GroupId__in=student_groups)
            .prefetch_related("assets", "quizzes")
        )

        project_data = []
        for project in projects:
            # Get quiz submissions for this project
            submissions = ReflectiveQuizSubmission.objects.filter(
                student=student,
                quiz__in=project.quizzes.all()
            )

            # Check if all quizzes are correctly answered
            total_quizzes = project.quizzes.count()
            completed_submissions = submissions.filter(is_correct=True).count()
            is_completed = completed_submissions == total_quizzes

            # Prepare submission data with additional options
            submission_data = []
            for submission in submissions:
                quiz = submission.quiz

                # Map selected options to values
                selected_values = [
                    quiz.options.get(str(option), "Invalid Option")
                    for option in submission.selected_options
                ]

                # Map all options for the quiz
                all_options = [{"index": key, "value": value} for key, value in quiz.options.items()]

                # Prepare detailed submission info
                submission_data.append({
                    "quiz_id": quiz.id,
                    "question": quiz.question,
                    "selected_options": selected_values,
                    "is_correct": submission.is_correct,
                    "all_options": all_options,
                    "correct_answers": [quiz.options.get(str(index), "Invalid Option") for index in quiz.answers]
                })

            # Serialize project data and add detailed submissions
            serializer = StudentClassroomProjectSerializer(project)
            project_info = serializer.data
            project_info['submitted_quizzes'] = submission_data
            project_info['is_completed'] = is_completed

            project_data.append(project_info)

        return Response(project_data, status=status.HTTP_200_OK)
    
class StudentProjectDetailView(APIView):
    permission_classes = [IsSpecificStudent]

    def get(self, request, project_id, *args, **kwargs):
        student = request.user  # Assuming `request.user` is a Student

        # Check if the student belongs to any group
        student_groups = UserGroup.objects.filter(user=student).values_list('GroupId', flat=True)
        if not student_groups.exists():
            return Response(
                {"error": "No groups assigned to this student."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve the project only if it belongs to the student's group
        project = (
            ClassroomProject.objects
            .filter(id=project_id, group__GroupId__in=student_groups)
            .prefetch_related("assets", "quizzes")
            .first()
        )

        if not project:
            return Response(
                {"error": "Project not found or not accessible to this student."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch quiz submissions for this project
        submissions = ReflectiveQuizSubmission.objects.filter(
            student=student,
            quiz__in=project.quizzes.all()
        )

        # Check completion status
        total_quizzes = project.quizzes.count()
        completed_submissions = submissions.filter(is_correct=True).count()
        is_completed = completed_submissions == total_quizzes

        # Serialize project data
        project_info = StudentClassroomProjectSerializer(project).data
        project_info['submitted_quizzes'] = ReflectiveQuizSubmissionSerializer(submissions, many=True).data
        project_info['is_completed'] = is_completed

        return Response(project_info, status=status.HTTP_200_OK)     

class ReflectiveQuizSubmissionView(APIView):
    permission_classes = [IsSpecificStudent]

    def post(self, request, *args, **kwargs):
        student = request.user  # Assuming request.user is a student
        data = request.data.get("submissions", [])

        if not data:
            return Response(
                {"error": "No submissions provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        feedback = []
        for submission in data:
            quiz_id = submission.get("quiz_id")
            selected_options = submission.get("selected_options", [])  # Expecting a list

            try:
                # Fetch the quiz
                quiz = ReflectiveQuiz.objects.get(id=quiz_id)

                # Validate selected options
                if not isinstance(selected_options, list):
                    return Response(
                        {"error": f"Selected options must be a list for quiz ID {quiz_id}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Determine correctness
                correct_answers = quiz.answers  # List of correct indices
                is_correct = sorted(selected_options) == sorted(correct_answers)

                # Save the submission with multi-select options
                ReflectiveQuizSubmission.objects.create(
                    student=student,
                    quiz=quiz,
                    selected_options=selected_options,
                    is_correct=is_correct
                )

                # Prepare feedback
                selected_values = [
                    quiz.options.get(str(option_index), "Invalid Option")
                    for option_index in selected_options
                ]

                correct_values = [
                    quiz.options.get(str(answer_index), "Invalid Option")
                    for answer_index in correct_answers
                ]

                feedback.append({
                    "quiz_id": quiz_id,
                    "question": quiz.question,
                    "selected_options": selected_values,
                    "is_correct": is_correct,
                    "correct_answers": correct_values
                })

            except ReflectiveQuiz.DoesNotExist:
                feedback.append({
                    "quiz_id": quiz_id,
                    "error": "Quiz not found."
                })

        return Response(
            {"feedback": feedback},
            status=status.HTTP_200_OK
        )

class ReflectiveQuizCompletionCountView(APIView):
    permission_classes = [IsSpecificStudent]  # Ensure user is authenticated

    def get(self, request, *args, **kwargs):
        student = request.user  # Logged-in student
        # Get the count of completed reflective quizzes
        completed_count = ReflectiveQuizSubmission.objects.filter(
            student=student,
            is_correct=True
        ).count()

        response_data = {
            "student_id": str(student.id),
            "completed_quizzes_count": completed_count
        }

        return Response(response_data, status=status.HTTP_200_OK)