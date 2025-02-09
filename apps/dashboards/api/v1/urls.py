from django.urls import path
from .views import (
    AdminHomeView,
    TeacherHomeView,
    StudentHomeView,
)

urlpatterns = [
    path('admin/', AdminHomeView.as_view(), name='admin_dashboard'),
    path('teacher/', TeacherHomeView.as_view(), name='teacher_dashboard'),
    path('student/', StudentHomeView.as_view(), name='student_dashboard'),
]