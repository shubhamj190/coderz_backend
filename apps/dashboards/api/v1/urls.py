from django.urls import path
from .views import GetTeacherStudentsProjectReport, HomeView, StudentDashboardReportView

urlpatterns = [
    path("", HomeView.as_view(), name="dashboard"),
    path(
        "students-project-report/",
        GetTeacherStudentsProjectReport.as_view(),
        name="dashboard",
    ),
    path(
        "student/<str:student_id>/dashboard/",
        StudentDashboardReportView.as_view(),
        name="student-dashboard",
    ),
]
