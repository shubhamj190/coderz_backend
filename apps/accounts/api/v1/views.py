import base64
import logging
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.accounts.models.grades import Division, Grade
from apps.accounts.tasks import process_bulk_upload_students
from apps.accounts.utils import user_name_creator
from core.middlewares.global_pagination import StandardResultsSetPagination
from core.permissions.role_based import IsSpecificAdmin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from templated_email import send_templated_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from .serializers import (
    DivisionSerializer,
    GradeSerializer,
    StudentCreateSerializer,
    StudentDetailSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
    TeacherCreateSerializer,
    TeacherDetailSerializer,
    TeacherListSerializer,
    CustomTokenObtainPairSerializer
)

from apps.accounts.models.user import User, UserDetails

logger = logging.getLogger(__name__)

# Login API views

class UnifiedLoginView(TokenObtainPairView):
    """
    A unified login view for all user types.
    
    Optionally, the client can include a "login_as" field in the request body
    (with values like "admin", "teacher", or "student") to enforce role-specific login.
    """
    # Use the base serializer which returns user info in serializer.user
    serializer_class = CustomTokenObtainPairSerializer  

    def post(self, request, *args, **kwargs):
        # Optionally extract role filter from request data.
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Instead of calling authenticate again, we get the user from the serializer.
        user = serializer.user
        
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens for the user.
        refresh = RefreshToken.for_user(user)
        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.details.UserType if hasattr(user, 'details') and user.details else None,
            "user_id": user.UserId
        }
        return Response(response_data, status=status.HTTP_200_OK)


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
    Expects a refresh token in the request body and blacklists it,
    ensuring that the token belongs to the currently authenticated user.
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
            # Verify the token's user_id matches the authenticated user.
            if token.payload.get("user_id") != request.user.UserId:
                return Response(
                    {"error": "The token does not belong to the authenticated user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            token.blacklist()
            return Response(
                {"message": "Logout successful."},
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
        if user.role != "admin":
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
    queryset = UserDetails.objects.all()
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class TeacherListAPIView(generics.ListAPIView):
    """
    API view to list all teachers.
    Accessible only by admin users.
    """
    queryset = UserDetails.objects.all()
    serializer_class = TeacherListSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]
    pagination_class = StandardResultsSetPagination

class TeacherDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve a single teacher's details and update them.
    The UserName field is read-only and cannot be updated.
    Access is restricted to admin users.
    """
    queryset = UserDetails.objects.all()
    serializer_class = TeacherDetailSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class AdminAddStudentAPIView(generics.CreateAPIView):
    """
    API endpoint for admin users to add a new student.
    This creates both a User record (with role 'student') and a Student profile.
    """
    queryset = UserDetails.objects.all()
    serializer_class = StudentCreateSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

class StudentListAPIView(generics.ListAPIView):
    """
    API view to list all students.
    Accessible only by admin users.
    """
    queryset = UserDetails.objects.all()
    serializer_class = StudentListSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]
    pagination_class = StandardResultsSetPagination

class StudentDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve a single teacher's details and update them.
    The UserName field is read-only and cannot be updated.
    Access is restricted to admin users.
    """
    queryset = UserDetails.objects.all()
    serializer_class = StudentDetailSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]

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
        task = process_bulk_upload_students.delay(csv_data)
        return Response({"message": "Bulk upload initiated.", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)