# apps/accounts/api/v1/urls.py
from django.urls import path
from apps.common.api.v1 import views

urlpatterns = [
    path('bulk-schedule-upload/', views.BulkUploadScheduleAPIView.as_view(), name='bulk_schedule_upload'),
]