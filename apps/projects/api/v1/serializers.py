# apps/accounts/api/v1/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.accounts.models.grades import Division, Grade
from apps.accounts.models.user import GroupMaster, TeacherLocationDetails
from apps.projects.models.projects import ClassroomProject, ProjectAsset, ProjectSession, ProjectSubmission, ReflectiveQuiz
from apps.projects.utils import get_teacher_for_grade_division

User = get_user_model()

class ProjectAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField()  # Ensure file is properly handled

    class Meta:
        model = ProjectAsset
        fields = ['id', 'file', 'file_type']

    def create(self, validated_data):
        """
        Create ProjectAsset instance and return it.
        """
        return ProjectAsset.objects.create(**validated_data)
    


class ReflectiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflectiveQuiz
        fields = ['id', 'question', 'options', 'answers', 'multiselect']

    def create(self, validated_data):
        """
        Create ReflectiveQuiz instance and return it.
        """
        return ReflectiveQuiz.objects.create(**validated_data)

class ClassroomProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(required=False)  # Allows file upload
    due_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    class Meta:
        model = ClassroomProject
        fields = ['id', 'title', 'description', 'grade', 'division', 'assigned_teacher', 'thumbnail', 'due_date']
    
    def create(self, validated_data):
        grade=validated_data['grade'].GradeName
        division=validated_data['division'].DivisionName
        group_name=f"{grade} - {division}"
        print(group_name)
        # Automatically assign group and teacher
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
            grade=validated_data['grade'],
            division=validated_data['division'],
            thumbnail=validated_data.get('thumbnail'),
            due_date=validated_data['due_date'],
            group=group,
            assigned_teacher=assigned_teacher
        )

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