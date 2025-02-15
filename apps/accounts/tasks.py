# accounts/tasks.py
import csv
from io import StringIO
from datetime import datetime
from celery import shared_task
from django.db import transaction
from apps.accounts.models.user import User, Student
from apps.accounts.models.grades import Grade, Division

@shared_task
def process_bulk_upload_students(csv_data):
    """
    Process CSV data to bulk create/update student users.
    Expects a CSV string with the following headers:
    Name,Last Name,Gender,DOB,E-Mail,Grade,Division,Admission No.,Active Status
    """
    reader = csv.DictReader(StringIO(csv_data))
    success_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=1):
        first_name = row.get("Name", "").strip()
        last_name = row.get("Last Name", "").strip()
        gender = row.get("Gender", "").lower().strip()
        dob_str = row.get("DOB", "").strip()
        email = row.get("E-Mail", "").strip()
        grade_name = row.get("Grade", "").strip()
        division_name = row.get("Division", "").strip()
        admission_no = row.get("Admission No.", "").strip()
        active_str = row.get("Active Status", "True").strip()
        is_active = active_str.lower() in ["true", "1", "yes", "y"]

        # Validate required fields
        if not email:
            errors.append(f"Row {row_num}: Missing E-Mail.")
            continue
        if not first_name or not last_name:
            errors.append(f"Row {row_num}: Missing Name/Last Name.")
            continue
        try:
            date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Row {row_num}: Invalid DOB format '{dob_str}'. Expected YYYY-MM-DD.")
            continue

        # Get or create Grade and Division
        try:
            grade_obj, _ = Grade.objects.get_or_create(name=grade_name)
            division_obj, _ = Division.objects.get_or_create(grade=grade_obj, name=division_name)
        except Exception as e:
            errors.append(f"Row {row_num}: Error processing Grade/Division: {str(e)}")
            continue

        try:
            with transaction.atomic():
                # Create or update User (role 'student')
                user, created = User.objects.get_or_create(
                    Email=email,
                    defaults={
                        "role": "student",
                        "FirstName": first_name,
                        "LastName": last_name,
                        "gender": gender,
                    }
                )
                if not created:
                    # Update the user if it exists
                    user.FirstName = first_name
                    user.LastName = last_name
                    user.gender = gender
                    user.save()

                # Create or update Student record
                student, s_created = Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "date_of_birth": date_of_birth,
                        "grade": grade_obj,
                        "division": division_obj,
                        "admission_number": admission_no,
                        "is_active": is_active,
                    }
                )
                if not s_created:
                    student.date_of_birth = date_of_birth
                    student.grade = grade_obj
                    student.division = division_obj
                    student.admission_number = admission_no
                    student.is_active = is_active
                    student.save()

                success_count += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            continue

    return {"success_count": success_count, "errors": errors}
