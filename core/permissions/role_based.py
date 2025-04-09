from rest_framework.permissions import BasePermission

from apps.accounts.models.user import UserDetails, UsersIdentity


class IsSpecificAdmin(BasePermission):

    def has_permission(self, request, view):
        return self._get_user_type(request) == "Admin"

    def _get_user_type(self, request):
        if not request.user.is_authenticated:
            return None

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return None

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return None

        return user_details.UserType


class IsSpecificTeacher(BasePermission):

    def has_permission(self, request, view):
        return self._get_user_type(request) == "Teacher"

    def _get_user_type(self, request):
        if not request.user.is_authenticated:
            return None

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return None

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return None

        return user_details.UserType


class IsSpecificStudent(BasePermission):

    def has_permission(self, request, view):
        return self._get_user_type(request) == "Learner"

    def _get_user_type(self, request):
        if not request.user.is_authenticated:
            return None

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return None

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return None

        return user_details.UserType


class IsAdminOrTeacher(BasePermission):

    def has_permission(self, request, view):
        return self._get_user_type(request) in ["Admin", "Teacher"]

    def _get_user_type(self, request):
        if not request.user.is_authenticated:
            return None

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return None

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return None

        return user_details.UserType

class IsAdminTeacherStudent(BasePermission):

    def has_permission(self, request, view):
        return self._get_user_type(request) in ["Admin", "Teacher", "Learner"]

    def _get_user_type(self, request):
        if not request.user.is_authenticated:
            return None

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return None

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return None

        return user_details.UserType