# schedules/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions.role_based import IsSpecificAdmin # Or your admin permission
from apps.common.tasks import process_bulk_schedule_upload

class BulkUploadScheduleAPIView(APIView):
    """
    API endpoint to bulk upload schedule data from an XLSX file.
    Expected file columns:
    Day, Grade, Section, 07:30:00-08:15:00, 08:15:00-09:00:00, ..., 15:45:00-16:30:00
    """
    permission_classes = [IsSpecificAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        academic_year = request.data.get("academic_year", "2024-2025")  # default or provided academic year
        file_obj = request.FILES.get("file", None)
        if not file_obj:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read the file's binary content.
            xlsx_data = file_obj.read()
        except Exception as e:
            return Response({"error": f"Error reading file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Enqueue the task asynchronously.
        task = process_bulk_schedule_upload.delay(xlsx_data, academic_year)
        return Response({"message": "Bulk schedule upload initiated.", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)
