from django.contrib.auth.backends import ModelBackend
from apps.accounts.models.user import User

class RoleBasedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user:
            return user
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.role == 'admin':
            return True
        return super().has_perm(user_obj, perm, obj)