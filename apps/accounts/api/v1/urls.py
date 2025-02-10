from django.urls import path
from .views import (
    AdminForgotPasswordAPIView,
    AdminLoginView,
    AdminLogoutView,
    AdminSignupView,
    DivisionListCreateAPIView,
    DivisionRetrieveUpdateDestroyAPIView,
    GradeListCreateAPIView,
    GradeRetrieveUpdateDestroyAPIView,
    ResetPasswordAPIView,
    StudentForgotPasswordAPIView,
    StudentLogoutView,
    TeacherForgotPasswordAPIView,
    TeacherLoginView,
    StudentLoginView,
    StudentSSOLoginView,
    TeacherLogoutView,
    TeacherSignupView,

)

urlpatterns = [
    # login endpoints
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('teacher/login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('student/login/', StudentLoginView.as_view(), name='student_login'),
    path('student/sso-login/', StudentSSOLoginView.as_view(), name='student_sso_login'),
    # signup endpoints
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('teacher/signup/', TeacherSignupView.as_view(), name='teacher-signup'),
    # logout endpoints
    path('admin/logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('teacher/logout/', TeacherLogoutView.as_view(), name='teacher-logout'),
    path('student/logout/', StudentLogoutView.as_view(), name='student-logout'),
    # forgot password endpoints
    path('forgot-password/admin/', AdminForgotPasswordAPIView.as_view(), name='admin-forgot-password'),
    path('forgot-password/teacher/', TeacherForgotPasswordAPIView.as_view(), name='teacher-forgot-password'),
    path('forgot-password/student/', StudentForgotPasswordAPIView.as_view(), name='student-forgot-password'),
    # The reset password endpoint accepts uidb64 and token as URL parameters.
    path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset-password'),
    # Grade endpoints
    path('admin/grades/', GradeListCreateAPIView.as_view(), name='grade-list-create'),
    path('admin/grades/<int:pk>/', GradeRetrieveUpdateDestroyAPIView.as_view(), name='grade-detail'),
    
    # Division endpoints
    path('admin/divisions/', DivisionListCreateAPIView.as_view(), name='division-list-create'),
    path('admin/divisions/<int:pk>/', DivisionRetrieveUpdateDestroyAPIView.as_view(), name='division-detail'),

]