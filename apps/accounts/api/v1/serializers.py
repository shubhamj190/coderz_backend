# apps/accounts/api/v1/auth/serializers.py
from django.forms import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models.grades import GradeDivisionMapping
from apps.accounts.models.user import GroupMaster, Location, TeacherLocationDetails, UserDetails, User, UserGroup
from apps.accounts.models import Grade, Division
from django.db import transaction

from apps.accounts.utils import user_name_creator

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
    # Fields for creating the related User record
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=UserDetails.GENDER_CHOICES, write_only=True)

    # Additional fields
    contact = serializers.CharField(write_only=True, required=False, allow_blank=True)
    alternative_contact = serializers.CharField(write_only=True, required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    grade_division_mapping = serializers.JSONField(write_only=True)

    class Meta:
        model = UserDetails
        fields = [
            "email", "password", "first_name", "last_name", "gender", 
            "contact", "alternative_contact",
            "is_active","grade_division_mapping"
        ]

    def create(self, validated_data):
        try:
            email = validated_data.pop("email")
            password = validated_data.pop("password")
            first_name = validated_data.pop("first_name")
            last_name = validated_data.pop("last_name")
            gender = validated_data.pop("gender")
            contact = validated_data.pop("contact", None)
            alternative_contact = validated_data.pop("alternative_contact", None)
            is_active = validated_data.pop("is_active", True)
            grade_division_mapping = validated_data.pop("grade_division_mapping", {})

            with transaction.atomic():
                # Ensure the email does not already exist
                if User.objects.filter(Email__iexact=email).exists():
                    raise serializers.ValidationError({"error": "A user with this email already exists."})

                # Create the user
                user = User.objects.create_user(
                    UserName=None,  # auto-generated
                    Email=email,
                    password=password,
                    InstitutionId=1
                )

                # Create UserDetails record
                details = UserDetails.objects.create(
                    user=user,
                    FirstName=first_name,
                    LastName=last_name,
                    Gender=gender,
                    ContactNo=contact,
                    AdditionalContactNo=alternative_contact,
                    UserType="Teacher",
                    IsActive=is_active,
                )

                # Generate a unique username
                user_name = user_name_creator("Teacher", user)
                user.UserName = user_name
                user.save()

                # Process grade-division mapping
                teacher_location_details = []
                for grade, divisions in grade_division_mapping.items():
                    for division in divisions:
                        group_name = f"{grade} - {division}"
                        group = GroupMaster.objects.filter(GroupName=group_name).first()

                        if group:
                            teacher_location_details.append(TeacherLocationDetails(
                                UserId=user.UserId,
                                InstitutionId=2,
                                LocationId=2,
                                GroupId=group.GroupId,
                                LID=Location.objects.get(LID=2),
                                GID=GroupMaster.objects.get(GroupId=group.GroupId),
                            ))
                # Bulk create TeacherLocationDetails
                TeacherLocationDetails.objects.bulk_create(teacher_location_details)

            return details
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

    
class TeacherListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    email = serializers.CharField(source="user.Email", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)
    UserId = serializers.CharField(source="user.UserId", read_only=True)
    userType = serializers.CharField(source="UserType", read_only=True)
    IsActive = serializers.CharField(source="user.IsActive", read_only=True)

    class Meta:
        model = UserDetails
        fields = ['full_name', 'email', 'UserId', 'UserName', 'gender', 'userType','IsActive']

    def get_full_name(self, obj):
        first = obj.FirstName or ""
        last = obj.LastName or ""
        return f"{first} {last}".strip()
    
class TeacherDetailSerializer(serializers.ModelSerializer):
    # Fields from the related User model
    FirstName = serializers.CharField(required=True)
    LastName = serializers.CharField(required=True)
    Gender = serializers.CharField(required=True)
    email = serializers.CharField(source="user.Email", read_only=True)
    UserId = serializers.CharField(source="user.UserId", read_only=True)
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    IsActive = serializers.BooleanField(source="user.IsActive", read_only=True)

    # Accept grade-division mapping from frontend
    grade_division_mapping = serializers.SerializerMethodField()
    grade_division_mapping_update = serializers.JSONField(write_only=True)

    class Meta:
        model = UserDetails
        fields = [
            "UserName",
            "UserId",
            "FirstName",
            "LastName",
            "email",
            "Gender",
            "IsActive",
            "grade_division_mapping",
            "grade_division_mapping_update",
        ]
    def get_grade_division_mapping(self, obj):
        """Fetch grade and division mapping from TeacherLocationDetails"""
        mapping = {}

        # Fetch all related TeacherLocationDetails for the given teacher
        teacher_location_details = TeacherLocationDetails.objects.filter(UserId=obj.user.UserId)

        for entry in teacher_location_details:
            group = entry.GID  # Assuming `group` is a FK to `GroupMaster`
            if group:
                parts = group.GroupName.split(" - ", 1)  # Split into Grade and Division
                if len(parts) == 2:
                    grade_name, division_name = parts
                    if grade_name not in mapping:
                        mapping[grade_name] = []
                    mapping[grade_name].append(division_name)

        return mapping

    def update(self, instance, validated_data):
        user = instance.user
        user_data = validated_data.pop("user", {})
        
        # Update User model fields
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Extract grade-division mapping
        grade_division_mapping = validated_data.pop("grade_division_mapping_update", {})
        with transaction.atomic():
            # Update other fields in UserDetails
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # 🛑 Delete all existing mappings before inserting new ones
            TeacherLocationDetails.objects.filter(UserId=user.UserId).delete()

            # 🔄 Process grade-division mapping: Create fresh entries
            for grade, divisions in grade_division_mapping.items():
                for division in divisions:
                    group_name = f"{grade} - {division}"
                    group = GroupMaster.objects.filter(GroupName=group_name).first()
                    if not group:
                        continue  # Skip if no matching group found

                    # ✅ Create new TeacherLocationDetails entry
                    TeacherLocationDetails.objects.create(
                        UserId=user.UserId,
                        InstitutionId=2,
                        LocationId=2,
                        GroupId=group.GroupId,
                        LID=Location.objects.get(LID=2),
                        GID=GroupMaster.objects.get(GroupId=group.GroupId),
                    )

        return instance
    
class StudentCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=UserDetails.GENDER_CHOICES, write_only=True)

    GradeId = serializers.CharField(write_only=True)  # Accepting name instead of pk
    DivisionId = serializers.CharField(write_only=True)  # Accepting name instead of pk

    class Meta:
        model = UserDetails
        fields = [
            "date_of_birth",
            "GradeId",
            "AdmissionNo",
            "email",
            "first_name",
            "last_name",
            "gender",
            "DivisionId",
        ]

    def validate_GradeId(self, value):
        """ Convert Grade name to the corresponding Grade instance """
        try:
            return Grade.objects.get(GradeName=value)
        except Grade.DoesNotExist:
            raise serializers.ValidationError(f"Grade '{value}' does not exist.")

    def validate_DivisionId(self, value):
        """ Convert Division name to the corresponding Division instance """
        try:
            return Division.objects.get(DivisionName=value)
        except Division.DoesNotExist:
            raise serializers.ValidationError(f"Division '{value}' does not exist.")

    def create(self, validated_data):
        email = validated_data.pop("email")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        gender = validated_data.pop("gender")
        GradeId = validated_data.pop("GradeId")  # This is now a Grade instance
        DivisionId = validated_data.pop("DivisionId")  # This is now a Division instance
        date_of_birth = validated_data.pop("date_of_birth")
        admission_number = validated_data.pop("AdmissionNo")

        with transaction.atomic():
            if User.objects.filter(Email=email).exists():
                raise serializers.ValidationError({"error": "A user with this email already exists."})
            
            # Create User
            user = User.objects.create_user(
                UserName=None,
                Email=email,
                password="student@123",
                InstitutionId=1
            )

            # Create Student
            student = UserDetails.objects.create(
                user=user,
                FirstName=first_name,
                LastName=last_name,
                Gender=gender,
                date_of_birth=date_of_birth,
                GradeId=GradeId,  # Now correctly mapped
                AdmissionNo=admission_number,
                UserType='Learner',
                IsActive=True,
            )

            # Generate Username
            user_name = user_name_creator('Learner', user)
            user.UserName = user_name
            user.save()

            # Group Assignment Logic
            group_name = f"{GradeId.GradeName} - {DivisionId.DivisionName}"
            group = GroupMaster.objects.filter(GroupName=group_name).first()

            if group:
                location = Location.objects.get(LID=2)
                UserGroup.objects.create(
                    user=user,
                    LID=location,
                    GID=group,
                    IsDeleted=False
                )

        return student
    
class StudentListSerializer(serializers.ModelSerializer):
    UserId = serializers.CharField(source="user.UserId", read_only=True)
    full_name = serializers.SerializerMethodField()
    UserName = serializers.CharField(source="user.UserName", read_only=True)
    email = serializers.CharField(source="user.Email", read_only=True)

    IsActive = serializers.CharField(source="user.IsActive", read_only=True)

    class Meta:
        model = UserDetails
        fields = ['full_name', 'email','UserId', 'UserName', 'Gender', 'IsActive','GradeId','UserType']

    def get_full_name(self, obj):
        # Combine first and last names; adjust as needed.
        first = obj.FirstName or ""
        last = obj.LastName or ""
        return f"{first} {last}".strip()

class StudentDetailSerializer(serializers.ModelSerializer):
    # Nested user fields (read-only username)
    UserId = serializers.CharField(source="user.UserId", read_only=True)
    FirstName = serializers.CharField(required=False)
    LastName = serializers.CharField(required=False)
    Gender = serializers.CharField(required=True)
    Email = serializers.EmailField(source="user.Email", required=False)
    PhoneNumber = serializers.CharField(source="user.PhoneNumber", required=False)
    IsActive = serializers.BooleanField(source="user.IsActive", read_only=True)

    # Correct field names to match UserDetails model
    GradeId = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=True)

    # ❌ Remove DivisionId from response (only used for input)
    DivisionId = serializers.SerializerMethodField()

    class Meta:
        model = UserDetails
        fields = [
            "UserId",         # Student's primary key
            "FirstName",      # Updatable user first name
            "LastName",       # Updatable user last name
            "Gender",         # Updatable user gender
            "Email",          # Updatable user email
            "PhoneNumber",    # Updatable user phone number
            "date_of_birth",
            "GradeId",
            "AdmissionNo",
            "DivisionId",     # Used only for input
            "IsActive"        # Student's active status
        ]
        extra_kwargs = {"DivisionId": {"write_only": True}}  # Ensure it's used only for input

    def get_DivisionId(self, obj):
        """Fetch DivisionId from UserGroup → GroupMaster dynamically."""
        try:
            # Get the user's group
            user_group = UserGroup.objects.filter(user=obj.user.UserId).first()
            if user_group:
                group_master = user_group.GID  # GroupMaster object
                if group_master:
                    # Extract Division from GroupName (assuming format: "GradeName - DivisionName")
                    group_name_parts = group_master.GroupName.split(" - ")
                    if len(group_name_parts) > 1:
                        division_name = group_name_parts[1]
                        division = Division.objects.filter(DivisionName=division_name).first()
                        if division:
                            return division.DivisionId  # Return DivisionId
        except Exception as e:
            return None  # Return None if not found or error occurs
        return None

    def update(self, instance, validated_data):
        # Extract nested user data if provided.
        user_data = validated_data.pop("user", {})
        user = instance.user
        for attr, value in user_data.items():
            if attr == "UserName":  # Skip updating username
                continue
            setattr(user, attr, value)
        user.save()

        # Extract DivisionId (not stored in UserDetails)
        division = validated_data.pop("DivisionId", None)

        # Update Student-specific fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # ✅ Process Division Logic (if required)
        if division:
            group_name = f"{instance.GradeId.GradeName} - {division.DivisionName}"
            group = GroupMaster.objects.filter(GroupName=group_name).first()
            if group:
                UserGroup.objects.update_or_create(
                    user=user,
                    defaults={"GID": group, "IsDeleted": False}
                )

        return instance

class GradeDivisionMappingSerializer(serializers.ModelSerializer):
    grade = serializers.CharField()
    division = serializers.CharField()

    class Meta:
        model = GradeDivisionMapping
        fields = ['grade', 'division']

    def create(self, validated_data):
        grade_name = validated_data['grade'].upper()  # Convert to uppercase before saving
        division_name = validated_data['division'].upper()  # Convert to uppercase before saving
        
        grade, _ = Grade.objects.get_or_create(grade_name=grade_name)
        division, _ = Division.objects.get_or_create(name=division_name)

        return GradeDivisionMapping.objects.create(grade=grade, division=division)