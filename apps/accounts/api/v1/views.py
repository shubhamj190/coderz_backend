import base64
import logging
from django.shortcuts import get_object_or_404
import jwt
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.accounts.models.grades import Division, Grade, GradeDivisionMapping
from apps.accounts.tasks import process_bulk_upload_students
from apps.accounts.utils import UniversalAuthenticationHandeler, create_response, decrypt_AES_CBC, registerUser, user_name_creator
from core.middlewares.global_pagination import StandardResultsSetPagination
from core.permissions.role_based import IsSpecificAdmin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from templated_email import send_templated_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Prefetch
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate

from .serializers import (
    DivisionSerializer,
    GradeDivisionMappingSerializer,
    GradeSerializer,
    StudentCreateSerializer,
    StudentDetailSerializer,
    StudentListSerializer,
    TeacherCreateSerializer,
    TeacherDetailSerializer,
    TeacherListSerializer,
    CustomTokenObtainPairSerializer,
    UniversalAuthenticateUserSeralizer
)

from apps.accounts.models.user import GroupMaster, RolesV2, UserDetails, UserMaster, UserRoles, UsersIdentity
from apps.accounts.models.user import UsersIdentity as User

logger = logging.getLogger(__name__)

# Login API views

@api_view(["POST"])
@permission_classes([AllowAny])
def UniversalAuthenticator(request):
    try:
        with transaction.atomic():
            # {payload:{},Platform:0,1,2}
            data = request.data
            data = data.get("payload")
            seralizer = UniversalAuthenticateUserSeralizer(data=data)
            if not seralizer.is_valid():
                return create_response(
                    seralizer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            data = seralizer.data
            username = data.get("username")
            password = data.get("password")
            password = decrypt_AES_CBC(password)
            platform = data.get("platform")
            isLogger = data.get("isLogger")
            moduleName = data.get("moduleName")
            eventName = data.get("eventName")
            dataId = data.get("dataId")
            DeviceId = data.get("DeviceId")

            # verify  which api should be called
            Success, authenticated_data = UniversalAuthenticationHandeler(
                username=username,
                password=password,
                platform=platform,
                isLogger=isLogger,
                moduleName=moduleName,
                eventName=eventName,
                dataId=dataId,
                DeviceId=DeviceId,
            )
            if not Success:
                return authenticated_data
            # Check if user exists
            user = (
                UserMaster.objects.filter(username=username, IsDeleted=False)
                .values()
                .first()
            )
            # if no create new user else skip
            if not user:
                user_data = (
                    UsersIdentity.objects.filter(
                        UserName=username, IsActive=True, IsDeleted=False
                    )
                    .values()
                    .first()
                )
                user_data["username"] = username
                user_data["password"] = password
                registered_user, registered_user_instance = registerUser(user_data)
                if registered_user.status_code != 201:
                    return registered_user
                registered_user = registered_user.data.get("payload")
                # noe register role
                role_data = UserRoles.objects.filter(
                    UserId=user_data.get("UserId")
                ).values_list("RoleId__Id", flat=True)
                role_data = RolesV2.objects.get(Id=role_data[0])
                register_role_data = UserRoles.objects.create(
                    UserId=registered_user_instance, RoleId=role_data
                )
                register_role_data.save()
            # authenticate user ang generate token for python
            user = authenticate(username=username, password=password)
            if user is None:
                return create_response("Invalid login credentials")
            if platform==0:
                cid=authenticated_data.get("userId")
            elif platform==1:
                cid=authenticated_data.get("data")
                cid=cid.get("questToken")
                cid=jwt.decode(cid,options={"verify_signature":False})
                cid=cid.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier')
            else:
                cid=authenticated_data.get("token")
                cid=jwt.decode(cid,options={"verify_signature":False})
                cid=cid.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier')
            Token = RefreshToken.for_user(user)
            Token["id"] = user.id
            Token["username"] = user.username
            Token["cid"]=cid

            payload = {
                "username": user.username,
                "id": user.id,
                "token": {"refresh": str(Token), "access": str(Token.access_token)},
                "DotNetAuth": authenticated_data,
            }

            # if the user is authenicated get their role details
            # register user and the roles in django table.
            # generate token

            return create_response(
                message="User Authenticated Successfully",
                status=status.HTTP_202_ACCEPTED,
                payload=payload,
            )
    except Exception as e:
        logging.exception(e)
        return create_response(
            message="User Authentication Failed",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class StudentSSOLoginView(APIView):
    def post(self, request, mission_name=None):
        # Your SSO authentication logic here.
        user_info = request.data.get('userInfo')
        institution_id = user_info.get('institutionId')
        username = user_info.get('userName')

        if mission_name and mission_name.upper() == "CODING":
            username = self._process_username(username, institution_id)
            base64_username = base64.b64encode(username.encode()).decode()
            kms_url = f"https://kms.ict360.com/ict/student-login/207/{base64_username}"
            return Response({"redirect_url": kms_url}, status=status.HTTP_200_OK)

        return Response({"redirect_url": "/home/exp-missions"}, status=status.HTTP_200_OK)

    def _process_username(self, username, institution_id):
        if username.startswith('SNVV@'):
            return f"{username.split('@')[1]}.ict@{institution_id}.questplus.in"
        elif '@' in username:
            local_part = username.split('@')[0]
            return f"{local_part}.ict@{institution_id}.questplus.in"
        return f"{username}.ict@{institution_id}.questplus.in"

# Signup API views

class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', None)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender = data.get('gender', None)

        if not email or not password:
            return Response(
                {"error": "Missing required fields: email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(Email=email).exists():
            return Response(
                {"error": "Email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create the user (UserName auto-generated by the custom manager).
                user = User.objects.create_user(
                    UserName=None,
                    Email=email,
                    password=password,
                    PhoneNumber=phone,
                    InstitutionId=1
                )
                
                # Create the corresponding UserDetails record.
                user_details=UserDetails.objects.create(
                    user=user,
                    FirstName=first_name,
                    LastName=last_name,
                    Gender=gender,
                    UserType='Admin'
                    # Other fields can be left as defaults/null if not provided.
                )
                user.UserName=user_name_creator('Admin', user)
                user.save()
            # Prepare context for the welcome email.
            context = {
                "username": user.UserName,
                "first_name": user_details.FirstName,
                "last_name": user_details.LastName,
                'subject': 'Here is your Admin account details',
            }
            
            # Send the welcome email using send_templated_mail.
            send_templated_mail(
                template_name="admin_welcome",  # Your email template name
                recipient_list=[email],
                context=context,
                from_email=settings.DEFAULT_FROM_EMAIL
            )
            
        except Exception as e:
            logger.error(f"Admin signup error: {str(e)}")
            return Response(
                {"error": "Error creating user", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Admin signup successful"},
            status=status.HTTP_201_CREATED
        )

class TeacherSignupView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        # Your signup logic here.
        data = request.data

        UserName = data.get('UserName')
        email = data.get('email')
        password = data.get('password')
        PhoneNumber = data.get('phone', None)

        if not UserName or not email or not password:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the user already exists username
        if User.objects.filter(UserName=UserName).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the user already exists email
        if User.objects.filter(Email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(UserName, email, password, PhoneNumber=PhoneNumber, role='teacher')
        except Exception as e:
            logger.error(f"Teacher signup error: {str(e)}")
            return Response({"error": "Error creating user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Teacher signup successful"}, status=status.HTTP_201_CREATED)
    
# logout API views

class UnifiedLogoutView(APIView):
    """
    Unified logout view for all user roles.
    Expects a refresh token in the request body and verifies that it belongs
    to the currently authenticated user.
    Note: Since 'rest_framework_simplejwt.token_blacklist' has been removed,
    tokens will not be blacklisted server-side.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            # Compare user_id as strings
            if str(token.payload.get("user_id")) != str(request.user.UserId):
                return Response(
                    {"error": "The token does not belong to the authenticated user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Since token_blacklist is disabled, we cannot blacklist the token.
            # Instead, simply return a successful logout response.
            return Response(
                {"message": "Logout successful. Please remove the token client-side."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
# forgot password API views

class UnifiedForgotPasswordAPIView(APIView):
    """
    A unified forgot password view for all user roles.
    Expects a POST request with an "email" field.
    Looks up the user and, based on their role, sends a password reset email
    using the appropriate email template.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(Email=email)
        except User.DoesNotExist:
            # Do not reveal whether the email exists
            return Response({"message": "If the email is valid, you will receive password reset instructions."},
                            status=status.HTTP_200_OK)

        # Determine which email template to use based on the user's role
        role = user.role.lower()
        if role == "admin":
            template_name = "admin_forgot_password"
        elif role == "teacher":
            template_name = "teacher_forgot_password"
        elif role == "student":
            template_name = "student_forgot_password"
        else:
            template_name = "default_forgot_password"

        # Generate token and UID for password reset
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct the reset URL; ensure FRONTEND_URL is defined in your settings
        reset_url = f"{settings.FRONTEND_URL}/api/v1/accounts/reset-password/{uidb64}/{token}/"
        
        context = {
            "subject": "Password Reset",
            "username": user.UserName,
            "reset_url": reset_url,
            "user_role": user.role,
        }
        
        # Send the email using the templated email function.
        send_templated_mail(
            template_name=template_name,
            recipient_list=[user.Email],
            context=context,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        
        return Response(
            {"message": "If the email is valid, you will receive password reset instructions."},
            status=status.HTTP_200_OK
        )

# reset password API views

class ResetPasswordAPIView(APIView):
    """
    Resets the user's password.
    Expects the URL to include uidb64 and token.
    The request body must include "new_password" and "confirm_password".
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        
        if not new_password or not confirm_password:
            return Response(
                {"error": "Both new_password and confirm_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Decode the UID from the URL.
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set the new password.
        user.set_password(new_password)
        user.save()
        
        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )
    
class AdminChangePasswordView(APIView):
    """
    API for logged-in admins to change their password.
    """
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def post(self, request):
        user = request.user

        # Ensure the user is an admin
        if user.role != "Admin":
            return Response(
                {"error": "Only admins can change passwords."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        # Validate required fields
        if not old_password or not new_password or not confirm_password:
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the old password is correct
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if new passwords match
        if new_password != confirm_password:
            return Response(
                {"error": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password strength (Optional: Add regex for complexity)
        if len(new_password) < 8:
            return Response(
                {"error": "New password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK
        )
# Grade Views
class GradeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all grades.
    POST: Create a new grade.
    Access restricted to admin users.
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class GradeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a grade by pk.
    PUT/PATCH: Update a grade.
    DELETE: Delete a grade.
    Access restricted to admin users.
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

# Division Views
class DivisionListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all divisions.
    POST: Create a new division.
    Access restricted to admin users.
    """
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class DivisionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a division by pk.
    PUT/PATCH: Update a division.
    DELETE: Delete a division.
    Access restricted to admin users.
    """
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class AdminAddTeacherAPIView(generics.CreateAPIView):
    """
    API endpoint for admin users to add a new teacher.
    This creates both the user record (with role 'teacher' and gender) and the teacher profile.
    """
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsSpecificAdmin]

class TeacherListAPIView(generics.ListAPIView):
    """
    API view to list all teachers.
    Accessible only by admin users.
    """
    serializer_class = TeacherListSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Return only teacher records (assuming stored value is "Teacher")
        qs =  UserDetails.objects.filter(UserType__iexact='Teacher')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                qs = qs.filter(IsActive=True)
            elif is_active.lower() == 'false':
                qs = qs.filter(IsActive=False)
        return qs

class TeacherDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve a single teacher's details and update them.
    The UserName field is read-only and cannot be updated.
    Access is restricted to admin users.
    """
    serializer_class = TeacherDetailSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]
    def get_queryset(self):
        # Return only teacher records (assuming stored value is "Teacher")
        return UserDetails.objects.filter(UserType__iexact='Teacher')

class AdminAddStudentAPIView(generics.CreateAPIView):
    """
    API endpoint for admin users to add a new student.
    This creates both a User record (with role 'student') and a Student profile.
    """
    serializer_class = StudentCreateSerializer
    permission_classes = [IsSpecificAdmin]

class StudentListAPIView(generics.ListAPIView):
    """
    API view to list all students.
    Accessible only by admin users.
    """
    serializer_class = StudentListSerializer
    permission_classes = [IsSpecificAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Return only teacher records (assuming stored value is "Teacher")
        qs = UserDetails.objects.filter(UserType__iexact='Learner')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                qs = qs.filter(IsActive=True)
            elif is_active.lower() == 'false':
                qs = qs.filter(IsActive=False)
        return qs

class StudentDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve a single teacher's details and update them.
    The UserName field is read-only and cannot be updated.
    Access is restricted to admin users.
    """
    serializer_class = StudentDetailSerializer
    permission_classes = [IsSpecificAdmin]

    def get_queryset(self):
        return UserDetails.objects.filter(UserType__iexact='Learner')

class BulkUploadStudentsAPIView(APIView):
    """
    API endpoint to bulk upload students from a CSV file.
    The CSV must have the columns:
    Name,Last Name,Gender,DOB,E-Mail,Grade,Division,Admission No.,Active Status
    """
    permission_classes = [IsSpecificAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file", None)
        if not csv_file:
            return Response({"error": "No CSV file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            csv_data = csv_file.read().decode("utf-8-sig")
        except Exception as e:
            return Response({"error": f"Failed to read CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Enqueue the task asynchronously
        task = process_bulk_upload_students(csv_data)
        return Response({"message": "Bulk upload initiated.", "task_id": "task.id"}, status=status.HTTP_202_ACCEPTED)
    
class GradeDivisionMappingAPIView(APIView):
    
    def get(self, request):
        """
        Fetch all grade-division mappings with required response structure.
        """
        grades = Grade.objects.prefetch_related(
            Prefetch(
                'grade_division_mappings',
                queryset=GradeDivisionMapping.objects.select_related('Division'),
                to_attr='divisions_list'
            )
        )

        response_data = []
        for grade in grades:
            divisions = [mapping.Division.DivisionName for mapping in grade.divisions_list]
            response_data.append({
                "id": grade.id,
                "class": str(grade.GradeId),
                "status": 1,
                "grade": grade.GradeName,
                "class_name": grade.GradeName,
                "divisions": ",".join(divisions)
            })

        return Response(response_data, status=status.HTTP_200_OK)

    
    def post(self, request):
        """
        Create a new Grade-Division mapping and automatically generate GroupMaster entries.
        """
        grade_name = request.data.get("grade", "").strip().upper()
        divisions = request.data.get("divisions", [])

        if not grade_name or not divisions:
            return Response({"error": "Grade and Divisions are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert division names to uppercase and remove duplicates
        division_names = list(set([d.strip().upper() for d in divisions if d.strip()]))

        try:
            with transaction.atomic():
                # Ensure the grade exists
                grade, _ = Grade.objects.get_or_create(GradeName=grade_name)

                added_divisions = []
                created_groups = []

                for div_name in division_names:
                    division, _ = Division.objects.get_or_create(DivisionName=div_name)
                    mapping, created = GradeDivisionMapping.objects.get_or_create(Grade=grade, Division=division)
                    
                    if created:
                        added_divisions.append(div_name)

                        # Create GroupMaster entry for each (Grade, Division) pair
                        group_name = f"{grade.GradeName} - {div_name}"
                        group_short_name = f"{grade.GradeName} - {div_name}"
                        
                        group_master, group_created = GroupMaster.objects.get_or_create(
                            GroupName=group_name,
                            defaults={
                                "GroupShortName": group_short_name,
                                "LocationId": 2,  # Adjust as needed
                                "IsActive": True,
                                "IsDeleted": False,
                                "ClassId": grade.id,
                                "SubClassId": 1,  # Adjust if needed
                                "SequenceNo": None,
                                "ModifiedOn": now()
                            }
                        )
                        
                        if group_created:
                            created_groups.append(group_name)

                return Response({
                    "message": "Divisions and GroupMaster entries added successfully",
                    "added_divisions": added_divisions,
                    "created_groups": created_groups
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def delete(self, request):
        """
        Delete a specific Grade-Division mapping.
        """
        grade_name = request.data.get("grade", "").strip().upper()
        division_name = request.data.get("division", "").strip().upper()

        if not grade_name or not division_name:
            return Response({"error": "Grade and Division are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grade = Grade.objects.get(GradeName=grade_name)
            division = Division.objects.get(DivisionName=division_name)

            deleted, _ = GradeDivisionMapping.objects.filter(Grade=grade, Division=division).delete()

            if deleted:
                return Response({"message": "Mapping deleted successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "Mapping not found"}, status=status.HTTP_404_NOT_FOUND)

        except Grade.DoesNotExist:
            return Response({"error": "Grade not found"}, status=status.HTTP_404_NOT_FOUND)
        except Division.DoesNotExist:
            return Response({"error": "Division not found"}, status=status.HTTP_404_NOT_FOUND)
        
class SingleGradeDivisionMappingAPIView(APIView):

    def get(self, request, grade_id=None):
        """
        Retrieve divisions for a specific grade.
        """
        if not grade_id:
            return Response({"error": "Grade name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            grade = Grade.objects.get(GradeId=grade_id)  # Case-insensitive match
            divisions = GradeDivisionMapping.objects.filter(Grade=grade).values_list("Division__DivisionName", flat=True)
            
            return Response({
                "id": grade.id,
                "grade": grade.GradeName,
                "status": grade.IsActive,
                "class_name": grade.GradeName,
                "divisions": list(divisions)
            }, status=status.HTTP_200_OK)

        except Grade.DoesNotExist:
            return Response({"error": "Grade not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, grade_id=None):
        """
        Update divisions for a specific grade.
        """
        if not grade_id:
            return Response({"error": "Grade name is required"}, status=status.HTTP_400_BAD_REQUEST)

        divisions = request.data.get("divisions", [])
        if not isinstance(divisions, list) or not divisions:
            return Response({"error": "A valid list of divisions is required."}, status=status.HTTP_400_BAD_REQUEST)

        division_names = list(set([d.strip().upper() for d in divisions if d.strip()]))

        try:
            with transaction.atomic():
                grade = Grade.objects.get(GradeId=grade_id)  # Case-insensitive match

                # Remove old mappings
                GradeDivisionMapping.objects.filter(Grade=grade).delete()

                updated_divisions = []
                for div_name in division_names:
                    division, _ = Division.objects.get_or_create(DivisionName=div_name)
                    GradeDivisionMapping.objects.create(Grade=grade, Division=division)
                    updated_divisions.append(div_name)

                return Response({"message": "Divisions updated successfully", "updated_divisions": updated_divisions}, status=status.HTTP_200_OK)

        except Grade.DoesNotExist:
            return Response({"error": "Grade not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)