# apps/accounts/api/v1/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.accounts.models.user import GroupMaster, TeacherLocationDetails
from apps.projects.models.projects import ClassroomProject, ProjectAsset, ProjectSession, ProjectSubmission, ReflectiveQuiz
from apps.projects.utils import get_teacher_for_grade_division

User = get_user_model()

class ProjectAssetSerializer(serializers.ModelSerializer):
    asset_url = serializers.FileField(required=False)  # Allows file upload

    class Meta:
        model = ProjectAsset
        fields = ['id', 'asset_type', 'asset_url', 'uploaded_by']

class ReflectiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveQuiz
        fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

class ClassroomProjectSerializer(serializers.ModelSerializer):
    assets = ProjectAssetSerializer(many=True, required=False)
    quizzes = ReflectiveQuizSerializer(many=True, required=False)
    thumbnail = serializers.FileField(required=False)  # Allows file upload

    class Meta:
        model = ClassroomProject
        fields = ['id', 'title', 'description', 'grade', 'division', 'assigned_teacher', 'thumbnail', 'due_date', 'assets', 'quizzes']
    
    def create(self, validated_data):
        assets_data = validated_data.pop('assets', [])
        quizzes_data = validated_data.pop('quizzes', [])

        # Automatically assign group and teacher
        group = GroupMaster.objects.filter(grade=validated_data['grade'], division=validated_data['division']).first()
        if not group:
            raise serializers.ValidationError("No group found for the given grade and division.")

        assigned_teacher = TeacherLocationDetails.objects.filter(GroupId=group.GroupId).first()
        if not assigned_teacher:
            raise serializers.ValidationError("No assigned teacher found for the given group.")

        classroom_project = ClassroomProject.objects.create(
            **validated_data,
            group=group,
            assigned_teacher=assigned_teacher
        )

        # Handle Asset Uploads
        for asset in assets_data:
            ProjectAsset.objects.create(classroom_project=classroom_project, **asset)

        # Handle Quizzes
        for quiz in quizzes_data:
            ReflectiveQuiz.objects.create(classroom_project=classroom_project, **quiz)

        return classroom_project
    
class ProjectSessionSerializer(serializers.ModelSerializer):
    file_type = serializers.ReadOnlyField()  # To include file type in response

    class Meta:
        model = ProjectSession
        fields = "__all__"

class ProjectSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubmission
        fields = ["id", "project", "student", "submission_file", "submitted_at", "feedback", "marks_obtained"]
        read_only_fields = ["submitted_at", "feedback", "marks_obtained"]