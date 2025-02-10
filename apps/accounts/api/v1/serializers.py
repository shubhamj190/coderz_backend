# apps/accounts/api/v1/auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models.user import User
from apps.accounts.models import Grade, Division

class RoleSpecificSerializer:
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['role'] = user.role
        data['user_id'] = user.UserId
        return data

class AdminLoginSerializer(RoleSpecificSerializer, TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'admin':
            raise serializers.ValidationError("Admin access only")
        return data

class TeacherLoginSerializer(RoleSpecificSerializer, TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'teacher':
            raise serializers.ValidationError("Teacher access only")
        return data

class StudentLoginSerializer(RoleSpecificSerializer, TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'student':
            raise serializers.ValidationError("Student access only")
        return data
    
class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'