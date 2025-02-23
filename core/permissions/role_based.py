from rest_framework.permissions import BasePermission

class IsSpecificAdmin(BasePermission):
    
    def has_permission(self, request, view):
        print(request.user.is_authenticated)
        return request.user.is_authenticated and request.user.role == 'Admin'
    
class IsSpecificTeacher(BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Teacher'
    
class IsSpecificStudent(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Learner'