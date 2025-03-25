# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.projects.api.v1.views import (
    ClassroomProjectCreateView,
    ClassroomProjectViewSet,
    CreateProjectSessionView,
    ProjectSessionListView,
    ProjectSubmissionCreateView,
    UpdateProjectSessionView
    )

urlpatterns = [
    path('classroom-project/create/', ClassroomProjectCreateView.as_view(), name='create-classroom-project'),
    path('project/<int:pk>/', ClassroomProjectViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='project-detail'),
    path("project-sessions/create/", CreateProjectSessionView.as_view(), name="create_project_session"),
    path("project-sessions/update/<int:session_id>/", UpdateProjectSessionView.as_view(), name="update_project_session"),
    path("project-sessions/", ProjectSessionListView.as_view(), name="list_project_sessions"),
    path("project-submission/", ProjectSubmissionCreateView.as_view(), name="project_submission"),
]