from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AdminAddStudentAPIView,
    AdminAddTeacherAPIView,
    AdminChangePasswordView,
    AdminSignupView,
    BulkUploadStudentsAPIView,
    UniversalUsernameLoginAuthenticator,
    DivisionListCreateAPIView,
    DivisionRetrieveUpdateDestroyAPIView,
    GradeDivisionMappingAPIView,
    GradeListCreateAPIView,
    GradeRetrieveUpdateDestroyAPIView,
    ResetPasswordAPIView,
    SingleGradeDivisionMappingAPIView,
    StudentDetailAPIView,
    StudentListAPIView,
    TeacherDetailAPIView,
    TeacherListAPIView,
    StudentSSOLoginView,
    UnifiedForgotPasswordAPIView,
    UniversalAuthenticator,
    UnifiedLogoutView,
)

urlpatterns = [
    # auth endpoints
    path('login/', UniversalAuthenticator, name='login'),
    path('student-login/', UniversalUsernameLoginAuthenticator, name='decode-student-login'),
    path('student/sso-login/', StudentSSOLoginView.as_view(), name='student_sso_login'),
    path('logout/', UnifiedLogoutView.as_view(), name='logout'),
    path('forgot-password/', UnifiedForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('admin/change-password/', AdminChangePasswordView.as_view(), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
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
    path('admin/teachers/<str:pk>/', TeacherDetailAPIView.as_view(), name='teacher-detail'),

    path('admin/students/add/', AdminAddStudentAPIView.as_view(), name='admin-add-student'),
    path('admin/students/', StudentListAPIView.as_view(), name='student-list'),
    path('admin/students/<str:pk>/', StudentDetailAPIView.as_view(), name='student-detail'),
    path('admin/students-bulk-upload/', BulkUploadStudentsAPIView.as_view(), name='students-bulk-upload'),

    # gradedivision mapping
    path('admin/grade-division-mapping/', GradeDivisionMappingAPIView.as_view(), name='grade-division-mapping'),
    path('admin/single-grade-division/<str:grade_id>/', SingleGradeDivisionMappingAPIView.as_view(), name='grade-division-detail'),

]
