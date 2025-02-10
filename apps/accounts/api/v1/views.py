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
from core.permissions.role_based import IsSpecificAdmin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from templated_email import send_templated_mail
from django.conf import settings

from .serializers import (
    AdminLoginSerializer,
    DivisionSerializer,
    GradeSerializer,
    TeacherCreateSerializer,
    TeacherLoginSerializer,
    StudentLoginSerializer
)

from apps.accounts.models.user import Teacher, User

logger = logging.getLogger(__name__)

# Login API views

class BaseLoginView(TokenObtainPairView):
    """
    Base login view that uses the custom serializer (which is set on the subclasses)
    and returns a JWT response with role and user_id.
    """
    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Instead of calling authenticate() again, get the user from the serializer.
        user = serializer.user

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens for the user.
        refresh = RefreshToken.for_user(user)
        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
            "user_id": user.UserId
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AdminLoginView(BaseLoginView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # If the login is successful but the user's role isn't 'admin', block access.
        if response.status_code == 200 and response.data.get('role') != 'admin':
            return Response({"error": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        return response


class TeacherLoginView(BaseLoginView):
    serializer_class = TeacherLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and response.data.get('role') != 'teacher':
            return Response({"error": "Teacher access only"}, status=status.HTTP_403_FORBIDDEN)
        return response


class StudentLoginView(BaseLoginView):
    serializer_class = StudentLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and response.data.get('role') != 'student':
            return Response({"error": "Student access only"}, status=status.HTTP_403_FORBIDDEN)
        return response


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
        # Your signup logic here.
        data = request.data

        UserName = data.get('UserName')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', None)

        if not UserName or not email or not password:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the user already exists
        if User.objects.filter(UserName=UserName).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the user already exists email
        if User.objects.filter(Email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(UserName, email, password, PhoneNumber=phone, role='admin')
        except Exception as e:
            logger.error(f"Admin signup error: {str(e)}")
            return Response({"error": "Error creating user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Admin signup successful"}, status=status.HTTP_201_CREATED)

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

class BaseLogoutView(APIView):
    """
    Base logout view that expects a refresh token in the request data,
    verifies that it belongs to the authenticated user, and blacklists it.
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
            # Verify that the token's user_id matches the authenticated user.
            # Note: Make sure your SIMPLE_JWT settings use your custom field if needed.
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

class AdminLogoutView(BaseLogoutView):
    def post(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admin users can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)

class TeacherLogoutView(BaseLogoutView):
    def post(self, request, *args, **kwargs):
        if request.user.role != "teacher":
            return Response(
                {"error": "Only teacher users can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)
    
class StudentLogoutView(BaseLogoutView):
    def post(self, request, *args, **kwargs):
        if request.user.role != "student":
            return Response(
                {"error": "Only student users can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)
    
# forgot password API views

class BaseForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    """
    Base view for forgot password functionality.
    Expects a POST request with an "email" field.
    Generates a password reset token and sends an email using a templated email.
    Subclasses should set:
        - expected_role (e.g. "admin", "teacher", or "student")
        - template_name (the name of the email template to use)
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Look up the user by email.
            user = User.objects.get(Email=email)
        except User.DoesNotExist:
            # Return the same generic response to avoid email enumeration.
            return Response(
                {"message": "If the email is valid, you will receive password reset instructions."},
                status=status.HTTP_200_OK
            )

        # Verify that the user's role matches the expected role.
        if hasattr(self, "expected_role") and user.role != self.expected_role:
            return Response(
                {"error": "Invalid user type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate token and uid
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct the reset URL.
        # FRONTEND_URL should be defined in your settings.py, for example: "http://your-frontend-domain"
        reset_url = f"{settings.FRONTEND_URL}/api/v1/accounts/reset-password/{uidb64}/{token}/"
        
        # Prepare the context for the email template.
        context = {
            "username": user.UserName,
            "reset_url": reset_url,
            "user_role": user.role,
        }
        
        # Use the send_templated_email library.
        send_templated_mail(
            template_name=self.template_name,  # e.g., "admin_forgot_password"
            recipient_list=[user.Email],
            context=context,
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        
        return Response(
            {"message": "If the email is valid, you will receive password reset instructions."},
            status=status.HTTP_200_OK
        )


class AdminForgotPasswordAPIView(BaseForgotPasswordAPIView):
    expected_role = "admin"
    template_name = "admin_forgot_password"  # This should match your template file name/path


class TeacherForgotPasswordAPIView(BaseForgotPasswordAPIView):
    expected_role = "teacher"
    template_name = "teacher_forgot_password"


class StudentForgotPasswordAPIView(BaseForgotPasswordAPIView):
    expected_role = "student"
    template_name = "student_forgot_password"

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
    queryset = Teacher.objects.all()
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAuthenticated, IsSpecificAdmin]