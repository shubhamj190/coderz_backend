from django.urls import path
from .views import (
    AdminAddStudentAPIView,
    AdminAddTeacherAPIView,
    AdminChangePasswordView,
    AdminSignupView,
    BulkUploadStudentsAPIView,
    DivisionListCreateAPIView,
    DivisionRetrieveUpdateDestroyAPIView,
    GradeListCreateAPIView,
    GradeRetrieveUpdateDestroyAPIView,
    ResetPasswordAPIView,
    StudentDetailAPIView,
    StudentListAPIView,
    TeacherDetailAPIView,
    TeacherListAPIView,
    StudentSSOLoginView,
    TeacherSignupView,
    UnifiedForgotPasswordAPIView,
    UnifiedLoginView,
    UnifiedLogoutView,
)

urlpatterns = [
    # auth endpoints
    path('login/', UnifiedLoginView.as_view(), name='login'),
    path('student/sso-login/', StudentSSOLoginView.as_view(), name='student_sso_login'),
    path('logout/', UnifiedLogoutView.as_view(), name='logout'),
    path('forgot-password/', UnifiedForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('admin/change-password/', AdminChangePasswordView.as_view(), name='change-password'),
    # signup endpoints
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    # path('teacher/signup/', TeacherSignupView.as_view(), name='teacher-signup'),
    # Grade endpoints
    path('admin/grades/', GradeListCreateAPIView.as_view(), name='grade-list-create'),
    path('admin/grades/<int:pk>/', GradeRetrieveUpdateDestroyAPIView.as_view(), name='grade-detail'),
    
    # Division endpoints
    path('admin/divisions/', DivisionListCreateAPIView.as_view(), name='division-list-create'),
    path('admin/divisions/<int:pk>/', DivisionRetrieveUpdateDestroyAPIView.as_view(), name='division-detail'),
    path('admin/teachers/add/', AdminAddTeacherAPIView.as_view(), name='admin-add-teacher'),

    path('admin/teachers/', TeacherListAPIView.as_view(), name='teacher-list'),
    path('admin/teachers/<int:pk>/', TeacherDetailAPIView.as_view(), name='teacher-detail'),

    path('admin/students/add/', AdminAddStudentAPIView.as_view(), name='admin-add-student'),
    path('admin/students', StudentListAPIView.as_view(), name='student-list'),
    path('admin/students/<int:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),
    path('students/bulk-upload/', BulkUploadStudentsAPIView.as_view(), name='students-bulk-upload'),


]
