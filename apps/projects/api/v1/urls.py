# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.projects.api.v1.views import (
    ClassroomProjectViewSet
    )

urlpatterns = [
    path('admin/project/', ClassroomProjectViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-list'),
    # Retrieve, update, or delete a specific project by its primary key
    path('admin/project/<int:pk>/', ClassroomProjectViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='project-detail'),
]