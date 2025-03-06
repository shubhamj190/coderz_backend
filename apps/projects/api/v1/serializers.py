# apps/accounts/api/v1/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.projects.models.projects import ClassroomProject, ProjectSession, ProjectSubmission
from apps.projects.utils import get_teacher_for_grade_division

User = get_user_model()

class ClassroomProjectSerializer(serializers.ModelSerializer):
    # assigned_teacher is read-only since it is auto-assigned
    assigned_teacher = serializers.CharField(read_only=True)
    
    class Meta:
        model = ClassroomProject
        fields = [
            'id',
            'title',
            'description',
            'grade',
            'division',
            'assigned_teacher',
            'thumbnail',
            'date_created',
            'date_modified',
            'due_date',
        ]
        read_only_fields = ['assigned_teacher', 'date_created', 'date_modified']

    def create(self, validated_data):
        grade = validated_data.get('grade')
        division = validated_data.get('division')
        teacher = get_teacher_for_grade_division(grade, division)
        validated_data['assigned_teacher'] = teacher
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If grade or division are updated, re-assign teacher automatically
        if 'grade' in validated_data or 'division' in validated_data:
            grade = validated_data.get('grade', instance.grade)
            division = validated_data.get('division', instance.division)
            teacher = get_teacher_for_grade_division(grade, division)
            validated_data['assigned_teacher'] = teacher
        return super().update(instance, validated_data)
    
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