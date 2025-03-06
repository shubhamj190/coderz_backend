# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.projects.api.v1.views import (
    ClassroomProjectViewSet,
    CreateProjectSessionView,
    ProjectSessionListView,
    UpdateProjectSessionView
    )

urlpatterns = [
    path('project/', ClassroomProjectViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-list'),
    # Retrieve, update, or delete a specific project by its primary key
    path('project/<int:pk>/', ClassroomProjectViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='project-detail'),
    path("project-sessions/create/", CreateProjectSessionView.as_view(), name="create_project_session"),
    path("project-sessions/update/<int:session_id>/", UpdateProjectSessionView.as_view(), name="update_project_session"),
    path("project-sessions/", ProjectSessionListView.as_view(), name="list_project_sessions"),
]