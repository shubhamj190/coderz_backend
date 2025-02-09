# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.accounts.api.v1 import views

urlpatterns = [
    path('users/', views.UserViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-list'),
    
    path('users/<int:pk>/', views.UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-detail'),
]