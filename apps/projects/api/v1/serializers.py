# apps/accounts/api/v1/serializers.py
import json
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.accounts.models.grades import Division, Grade
from apps.accounts.models.user import GroupMaster, TeacherLocationDetails, UserGroup
from apps.projects.models.projects import ClassroomProject, ProjectAsset, ProjectSession, ProjectSubmission, ReflectiveQuiz, ReflectiveQuizSubmission
from apps.projects.utils import get_teacher_for_grade_division
from rest_framework import viewsets, status
from rest_framework.response import Response

User = get_user_model()

class ProjectAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAsset
        fields = ["id", "file_url", "file_type"]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

class UpdateProjectAssetsSerializer(serializers.Serializer):
    assets = serializers.ListField(child=serializers.JSONField(), required=False)
    asset_files = serializers.ListField(child=serializers.FileField(), required=False)

    def update(self, instance, validated_data):
            request = self.context.get("request")
            asset_files = request.FILES.getlist("asset_files", [])  # Uploaded files
            file_types_raw = request.POST.get('file_types')  # Get file types as a JSON string

            # Ensure `file_types_raw` is valid JSON and parse it
            try:
                file_types = json.loads(file_types_raw) if file_types_raw else []
            except json.JSONDecodeError:
                return Response({"error": "Invalid file_types format"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure assets and files match
            if len(file_types) != len(asset_files):
                raise serializers.ValidationError(
                    {"assets": "Mismatch between assets data and uploaded files."}
                )

            # **Delete old assets before updating**
            instance.assets.all().delete()

            # **Create new assets**
            new_assets = []
            for file_type, file in zip(file_types, asset_files):
                new_asset = ProjectAsset.objects.create(
                    project=instance,
                    file=file,
                    file_type=file_type  # Directly using file_type since it's a string
                )
                new_assets.append(new_asset)

            return instance


class ReflectiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveQuiz
        fields = ['id', 'question', 'options', 'answers', 'multiselect']

    def create(self, validated_data):
        """
        Create ReflectiveQuiz instance and return it.
        """
        return ReflectiveQuiz.objects.create(**validated_data)


class StudentAndTeacherProjectAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAsset
        fields = ["id", "file", "file_type", "uploaded_at"]
class StudentAndTeacherReflectiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveQuiz
        fields = ["id", "question", "options", "multiselect"]
class TeacherClassroomProjectSerializer(serializers.ModelSerializer):
    assets = StudentAndTeacherProjectAssetSerializer(many=True, read_only=True)
    quizzes = StudentAndTeacherReflectiveQuizSerializer(many=True, read_only=True)

    class Meta:
        model = ClassroomProject
        fields = ["id", "title", "description", "assets", "quizzes"]

class ReflectiveQuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveQuizSubmission
        fields = '__all__'

class StudentClassroomProjectSerializer(serializers.ModelSerializer):
    assets = StudentAndTeacherProjectAssetSerializer(many=True, read_only=True)
    quizzes = StudentAndTeacherReflectiveQuizSerializer(many=True, read_only=True)
    submitted_quizzes = ReflectiveQuizSubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = ClassroomProject
        fields = ["id", "title", "description", "assets", "quizzes", "grade", "division", "due_date", "thumbnail",'submitted_quizzes']

class ProjectSessionSerializer(serializers.ModelSerializer):
    file_type = serializers.ReadOnlyField()
    thumbnail = serializers.ImageField(use_url=True, required=False)  # Allow upload

    class Meta:
        model = ProjectSession
        fields = "__all__"

class ProjectSessionUpdateSerializer(serializers.ModelSerializer):
    file_type = serializers.ReadOnlyField()
    thumbnail = serializers.ImageField(use_url=True, required=False)  # Allow upload
    ppt_file = serializers.FileField(use_url=True, required=False)   # Allow upload

    class Meta:
        model = ProjectSession
        fields = "__all__"

class ProjectSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    grade_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectSubmission
        fields = ["id", "project", "student", "submission_file", "submitted_at", "feedback", "student_name", "grade_name","division_name","teacher_evaluation", "teacher",]
        read_only_fields = ["submitted_at"]

    # Fetch student's full name
    def get_student_name(self, obj):
        return f"{obj.student.FirstName} {obj.student.LastName}"
    
    # Fetch student's full name
    def get_teacher_name(self, obj):
        return f"{obj.teacher.FirstName} {obj.teacher.LastName}"

    # Fetch grade name
    def get_grade_name(self, obj):
        if obj.student.GradeId:
            grade=Grade.objects.filter(GradeId=obj.student.GradeId).first()
            return grade.GradeName if grade else None
        return None

    # Fetch division name
    def get_division_name(self, obj):
        user_group = UserGroup.objects.filter(user=obj.student.user).first()
        return user_group.GID.GroupName.split("-")[1].strip() if user_group and user_group.GID else None

class ClassroomProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(required=False)
    due_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    assets = StudentAndTeacherProjectAssetSerializer(many=True, read_only=True)
    quizzes = ReflectiveQuizSerializer(many=True, read_only=True)
    submitted_quizzes = ReflectiveQuizSubmissionSerializer(many=True, read_only=True)

    # Custom fields for GET request
    grade_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassroomProject
        fields = [
            'id', 'title', 'description', 'grade', 'division', 'assigned_teacher', 
            'thumbnail', 'due_date', 'assets', 'quizzes', 'submitted_quizzes',
            'grade_name', 'division_name'  # Include custom fields
        ]

    # Method to retrieve grade name
    def get_grade_name(self, obj):
        return obj.grade.GradeName if obj.grade else None

    # Method to retrieve division name
    def get_division_name(self, obj):
        return obj.division.DivisionName if obj.division else None

    def to_internal_value(self, data):
        data = data.copy()

        grade_name = data.get('grade')
        division_name = data.get('division')

        # Fetch Grade and Division objects using names
        grade = Grade.objects.filter(GradeName=grade_name).first()
        division = Division.objects.filter(DivisionName=division_name).first()

        if not grade:
            raise serializers.ValidationError({"grade": "Invalid grade name provided."})
        if not division:
            raise serializers.ValidationError({"division": "Invalid division name provided."})

        # Replace names with actual objects
        data['grade'] = grade.id
        data['division'] = division.DivisionId

        return super().to_internal_value(data)

    def create(self, validated_data):
        grade = validated_data['grade']
        division = validated_data['division']
        group_name = f"{grade.GradeName} - {division.DivisionName}"
        print(group_name)

        # Fetch group and teacher
        group = GroupMaster.objects.filter(GroupName=group_name).first()
        if not group:
            raise serializers.ValidationError("No group found for the given grade and division.")

        group_teacher = TeacherLocationDetails.objects.filter(GroupId=group.GroupId).first().UserId
        assigned_teacher = User.objects.filter(UserId=group_teacher).first()
        if not assigned_teacher:
            raise serializers.ValidationError("No assigned teacher found for the given group.")

        classroom_project = ClassroomProject.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            grade=grade,
            division=division,
            thumbnail=validated_data.get('thumbnail'),
            due_date=validated_data['due_date'],
            group=group,
            assigned_teacher=assigned_teacher
        )

        return classroom_project
    
class ProjectSubmissionEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = ['id', 'teacher_evaluation']
        read_only_fields = ['id']