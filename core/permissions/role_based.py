from rest_framework.permissions import BasePermission

from apps.accounts.models.user import UserDetails, UsersIdentity


class IsSpecificAdmin(BasePermission):

    def has_permission(self, request, view):
        print(request.user.is_authenticated)
        return request.user.is_authenticated and request.user.role == "Admin"


class IsSpecificTeacher(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Teacher"


class IsSpecificStudent(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user_identity = UsersIdentity.objects.filter(UserName=request.user.username).first()
        if not user_identity:
            return False

        user_details = UserDetails.objects.filter(UserId=user_identity.UserId).first()
        if not user_details:
            return False

        request.user.role = user_details.UserType
        return request.user.role == "Learner"


class IsAdminOrTeacher(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "Admin",
            "Teacher",
        ]

class IsAdminTeacherStudent(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "Admin",
            "Teacher",
            "Learner",
        ]