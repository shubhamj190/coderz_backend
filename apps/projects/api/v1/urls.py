# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.projects.api.v1.views import (
    ClassroomProjectCreateView,
    ClassroomProjectListView,
    ClassroomProjectRetrieveUpdateView,
    ProjectAssetCreateView,
    ReflectiveQuizCreateView,
    CreateProjectSessionView,
    ProjectSessionListView,
    ProjectSubmissionCreateView,
    ReflectiveQuizRetrieveUpdateAPIView,
    RetrieveUpdateProjectAssetsView,
    TeacherProjectsView,
    UpdateProjectSessionView
    )

urlpatterns = [
    path('classroom-projects/', ClassroomProjectCreateView.as_view(), name='create-classroom-project'),
    path("classroom-projects/<int:pk>/", ClassroomProjectRetrieveUpdateView.as_view(), name="retrieve-update-classroom-project"),
    path("classroom-projects/list/", ClassroomProjectListView.as_view(), name="admin-classroom-projects"),

    path('classroom-projects/<int:project_id>/assets/', ProjectAssetCreateView.as_view(), name='create-project-assets'),
    path("classroom-projects/<int:pk>/update-assets/", RetrieveUpdateProjectAssetsView.as_view(), name="retrieve-update-project-assets"),

    path('classroom-projects/<int:project_id>/quizzes/', ReflectiveQuizCreateView.as_view(), name='create-project-quizzes'),
    path("reflective-quiz/<int:id>/", ReflectiveQuizRetrieveUpdateAPIView.as_view(), name="reflective-quiz-detail"),

    path("project-sessions/create/", CreateProjectSessionView.as_view(), name="create_project_session"),
    path("project-sessions/update/<int:session_id>/", UpdateProjectSessionView.as_view(), name="update_project_session"),
    path("project-sessions/", ProjectSessionListView.as_view(), name="list_project_sessions"),
    path("project-submission/", ProjectSubmissionCreateView.as_view(), name="project_submission"),

    path("teacher/projects/", TeacherProjectsView.as_view(), name="teacher-projects"),
]