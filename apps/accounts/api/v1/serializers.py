# apps/accounts/api/v1/auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models.user import UserDetails, User
from apps.accounts.models import Grade, Division
from django.db import transaction

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user_id'] = user.UserId
        if hasattr(self.user, 'details') and self.user.details:
            data['role'] = self.user.details.UserType
        else:
            data['role'] = None
        return data
        return data
    
class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'

class TeacherCreateSerializer(serializers.ModelSerializer):
    # Fields for creating the related user record
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=UserDetails.GENDER_CHOICES, write_only=True)

    class Meta:
        model = UserDetails
        # Include teacher-specific fields as well as the extra user fields
        fields = [
            "assigned_grades",     # Expect a list of grade IDs
            "assigned_divisions",  # Expect a list of division IDs
            "email",
            "password",
            "first_name",
            "last_name",
            "gender"
        ]
    
    def create(self, validated_data):
        try:
            # Extract user-related data
            email = validated_data.pop("email")
            password = validated_data.pop("password")
            first_name = validated_data.pop("first_name")
            last_name = validated_data.pop("last_name")
            gender = validated_data.pop("gender")
            
            # Pop many-to-many fields (if provided)
            assigned_grades = validated_data.pop("assigned_grades", None)
            assigned_divisions = validated_data.pop("assigned_divisions", None)
            available_time_slots = validated_data.pop("available_time_slots", None)
            
            with transaction.atomic():
                # Create the user using the custom user manager.
                user = User.objects.create_user(
                    Email=email,
                    password=password,
                    role='teacher',  # Force the role to teacher
                    FirstName=first_name,
                    LastName=last_name,
                    gender=gender
                )
                
                # Create the Teacher record linking to the user.
                teacher = UserDetails.objects.create(user=user, **validated_data)
                
                # Assign many-to-many relationships using .set() if data is provided.
                if assigned_grades is not None:
                    teacher.assigned_grades.set(assigned_grades)
                if assigned_divisions is not None:
                    teacher.assigned_divisions.set(assigned_divisions)
                if available_time_slots is not None:
                    teacher.available_time_slots.set(available_time_slots)
        except Exception as e:
            # Raise a validation error so that the error gets returned in the API response.
            raise serializers.ValidationError({"error": str(e)})
        
        return teacher
    
class TeacherListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    email = serializers.CharField(source="user.Email", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)
    id = serializers.IntegerField(source="user.UserId", read_only=True)

    class Meta:
        model = UserDetails
        fields = ['full_name', 'email','id', 'UserName', 'gender', 'is_active']

    def get_full_name(self, obj):
        # Combine first and last names; adjust as needed.
        first = obj.user.FirstName or ""
        last = obj.user.LastName or ""
        return f"{first} {last}".strip()
    
class TeacherDetailSerializer(serializers.ModelSerializer):
    # Fields from the related User model
    FirstName = serializers.CharField(source="user.FirstName", required=False)
    LastName = serializers.CharField(source="user.LastName", required=False)
    gender = serializers.CharField(source="user.gender", required=False)
    Email = serializers.EmailField(source="user.Email", required=False)
    PhoneNumber = serializers.CharField(source="user.PhoneNumber", required=False)
    
    class Meta:
        model = UserDetails
        fields = [
            "id",               # Teacher's primary key
            "FirstName",        # Updatable user first name
            "LastName",         # Updatable user last name
            "gender",           # Updatable user gender
            "Email",            # Updatable user email
            "PhoneNumber",      # Updatable user phone number
            "years_of_experience",
            "assigned_grades",
            "assigned_divisions",
            # "available_time_slots"
            'is_active'
        ]
    
    def update(self, instance, validated_data):
        # Extract nested user data if present.
        user_data = validated_data.pop("user", {})
        
        # Update the user fields except for UserName.
        user = instance.user
        for attr, value in user_data.items():
            # Skip username update even if provided
            if attr == "UserName":
                continue
            setattr(user, attr, value)
        user.save()
        
        # Update Teacher-specific fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class StudentCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=UserDetails.GENDER_CHOICES, write_only=True)
    
    class Meta:
        model = UserDetails
        fields = [
            "date_of_birth",
            "grade",           # PK or instance of Grade
            "division",        # PK or instance of Division
            "roll_number",
            "parent_name",
            "parent_email",
            "parent_phone",
            "admission_number",
            "email",
            "password",
            "first_name",
            "last_name",
            "gender"
        ]
    
    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        gender = validated_data.get("gender")
        roll_number = validated_data.get("roll_number")
        grade = validated_data.get("grade")
        division = validated_data.get("division")
        date_of_birth = validated_data.get("date_of_birth")
        parent_name = validated_data.get("parent_name", "")
        parent_email = validated_data.get("parent_email", "")
        parent_phone = validated_data.get("parent_phone", "")
        admission_number = validated_data.get("admission_number")
        
        with transaction.atomic():
            # Create the User record with role 'student'
            user = User.objects.create_user(
                Email=email,
                password=password,
                role='student',
                FirstName=first_name,
                LastName=last_name,
                gender=gender,
                roll_number=roll_number,
                grade=grade,
                division=division
            )
            
            # Create the Student record linking to the user.
            student = UserDetails.objects.create(
                user=user,
                FirstName=first_name,
                LastName=last_name,
                date_of_birth=date_of_birth,
                grade=grade,
                division=division,
                roll_number=roll_number,
                parent_name=parent_name,
                parent_email=parent_email,
                parent_phone=parent_phone,
                admission_number=admission_number
            )
        return student
    
class StudentListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    email = serializers.CharField(source="user.Email", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)

    class Meta:
        model = UserDetails
        fields = ['full_name', 'email','id', 'UserName', 'gender', 'is_active','grade','division']

    def get_full_name(self, obj):
        # Combine first and last names; adjust as needed.
        first = obj.user.FirstName or ""
        last = obj.user.LastName or ""
        return f"{first} {last}".strip()

class StudentDetailSerializer(serializers.ModelSerializer):
    # Nested user fields (read-only username)
    FirstName = serializers.CharField(source="user.FirstName", required=False)
    LastName = serializers.CharField(source="user.LastName", required=False)
    gender = serializers.CharField(source="user.gender", required=False)
    Email = serializers.EmailField(source="user.Email", required=False)
    PhoneNumber = serializers.CharField(source="user.PhoneNumber", required=False)
    
    class Meta:
        model = UserDetails
        fields = [
            "id",                # Student's primary key
            "FirstName",         # Updatable user first name
            "LastName",          # Updatable user last name
            "gender",            # Updatable user gender
            "Email",             # Updatable user email
            "PhoneNumber",       # Updatable user phone number
            "date_of_birth",
            "grade",
            "division",
            "roll_number",
            "parent_name",
            "parent_email",
            "parent_phone",
            "admission_number",
            "is_active"          # Student's active status
        ]
    
    def update(self, instance, validated_data):
        # Extract nested user data if provided.
        user_data = validated_data.pop("user", {})
        user = instance.user
        for attr, value in user_data.items():
            # Skip updating the username even if provided.
            if attr == "UserName":
                continue
            setattr(user, attr, value)
        user.save()
        
        # Update Student-specific fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class StudentUpdateSerializer(serializers.ModelSerializer):
    # Nested user fields:
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    FirstName = serializers.CharField(source="user.FirstName", required=False)
    LastName = serializers.CharField(source="user.LastName", required=False)
    gender = serializers.CharField(source="user.gender", required=False)
    Email = serializers.EmailField(source="user.Email", required=False)
    PhoneNumber = serializers.CharField(source="user.PhoneNumber", required=False)

    class Meta:
        model = UserDetails
        fields = [
            "UserName",         # read-only, coming from the related User model
            "FirstName",        # updatable user first name
            "LastName",         # updatable user last name
            "gender",           # updatable user gender
            "Email",            # updatable user email
            "PhoneNumber",      # updatable user phone number
            "date_of_birth",
            "grade",
            "division",
            "roll_number",
            "parent_name",
            "parent_email",
            "parent_phone",
            "admission_number",
            "is_active"         # student-specific active flag
        ]
    
    def update(self, instance, validated_data):
        # Extract user data from nested input, if provided.
        user_data = validated_data.pop("user", {})
        user = instance.user

        # Update user fields except for UserName.
        for attr, value in user_data.items():
            if attr == "UserName":
                continue
            setattr(user, attr, value)
        user.save()
        
        # Update remaining student fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance