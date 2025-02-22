
from django.contrib import admin
from django.urls import path, include

api_patterns = [
    path('accounts/', include('apps.accounts.api.v1.urls')),
    # path('courses/', include('apps.courses.api.v1.urls')),
    # path('assessments/', include('apps.assessments.api.v1.urls')),
    # path('projects/', include('apps.projects.api.v1.urls')),
    # path('competitions/', include('apps.competitions.api.v1.urls')),
    # path('communications/', include('apps.communications.api.v1.urls')),
    # path('dashboards/', include('apps.dashboards.api.v1.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_patterns)),
    path('api/v2/', include(api_patterns)),  # We'll handle version differences in views
]
