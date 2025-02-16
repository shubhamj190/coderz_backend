# schedules/tasks.py
import csv
from io import StringIO
from datetime import datetime
from celery import shared_task
from django.db import transaction
from accounts.models import Grade, Division, Teacher
from courses.models import Course
from apps.common.models.scheduling import Schedule, ScheduleSlot, TimeSlot, WeekDay

@shared_task
def process_bulk_schedule_upload(xlsx_data, academic_year):
    """
    Process XLSX data (as a string) to bulk upload schedule.
    The XLSX file is expected to have the headers:
    Day, Grade, Section, 07:30:00-08:15:00, 08:15:00-09:00:00, ..., 15:45:00-16:30:00
    """
    # We use openpyxl to read XLSX data. Since the file content is passed as bytes/string,
    # we must use a BytesIO wrapper.
    from io import BytesIO
    import openpyxl

    wb = openpyxl.load_workbook(filename=BytesIO(xlsx_data), data_only=True)
    sheet = wb.active

    # Assume first row is header.
    headers = [cell.value for cell in sheet[1]]
    if len(headers) < 4 or headers[0] != "Day" or headers[1] != "Grade" or headers[2] != "Section":
        return {"error": "Invalid header format."}

    # Time slot headers are from column 4 onward.
    time_slot_headers = headers[3:]
    # Create a mapping of header -> TimeSlot instance
    time_slot_map = {}
    for header in time_slot_headers:
        try:
            ts = TimeSlot.objects.get(display_name=header)
            time_slot_map[header] = ts
        except TimeSlot.DoesNotExist:
            # Skip or log error if timeslot not configured.
            continue

    success_count = 0
    errors = []
    # Process rows starting from row 2.
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            day_val = row[0]
            grade_val = row[1]
            section_val = row[2]
            if not day_val or not grade_val or not section_val:
                errors.append(f"Row {idx}: Missing Day, Grade, or Section.")
                continue

            # Get WeekDay instance (assumes already created)
            try:
                weekday = WeekDay.objects.get(name=day_val)
            except WeekDay.DoesNotExist:
                errors.append(f"Row {idx}: WeekDay '{day_val}' not found.")
                continue

            # Get or create Grade and Division.
            grade_obj, _ = Grade.objects.get_or_create(name=grade_val)
            division_obj, _ = Division.objects.get_or_create(grade=grade_obj, name=section_val)

            # Get or create the Schedule record.
            schedule, _ = Schedule.objects.get_or_create(
                grade=grade_obj,
                section=division_obj,
                academic_year=academic_year,
                defaults={"is_active": True}
            )

            # Iterate over each time slot column.
            for col_idx, header in enumerate(time_slot_headers, start=3):
                cell_value = row[col_idx]
                if not cell_value or str(cell_value).strip() == "":
                    continue
                cell_text = str(cell_value).strip()
                teacher_obj = None
                course_obj = None

                if cell_text.lower() in ["break", "lunch"]:
                    # Get or create a Course for special slots.
                    course_obj, _ = Course.objects.get_or_create(name=cell_text.title())
                else:
                    # Assume cell_text is teacher's full name. Try to lookup Teacher by splitting the name.
                    names = cell_text.split()
                    if len(names) < 2:
                        errors.append(f"Row {idx}, Column '{header}': Invalid teacher name '{cell_text}'.")
                        continue
                    first_name = names[0]
                    last_name = names[-1]
                    teacher_qs = Teacher.objects.filter(user__FirstName__iexact=first_name, user__LastName__iexact=last_name)
                    if teacher_qs.exists():
                        teacher_obj = teacher_qs.first()
                        # Use teacher specialization as course name, or default to "Regular Class"
                        course_name = teacher_obj.specialization if teacher_obj.specialization else "Regular Class"
                        course_obj, _ = Course.objects.get_or_create(name=course_name)
                    else:
                        errors.append(f"Row {idx}, Column '{header}': Teacher '{cell_text}' not found.")
                        continue

                # Lookup the TimeSlot object for the header.
                time_slot_obj = time_slot_map.get(header)
                if not time_slot_obj:
                    errors.append(f"Row {idx}, Column '{header}': TimeSlot '{header}' not configured.")
                    continue

                # Create a ScheduleSlot record.
                with transaction.atomic():
                    ScheduleSlot.objects.create(
                        schedule=schedule,
                        day=weekday,
                        time_slot=time_slot_obj,
                        course=course_obj,
                        teacher=teacher_obj  # can be None if special slot
                    )
            success_count += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
            continue

    return {"success_count": success_count, "errors": errors}
