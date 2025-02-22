from apps.accounts.models.user import User
def user_name_creator(user_type, user):
    import pdb;pdb.set_trace()
    UserName = None
    if user_type == 'Learner':
            pass
            # For student users, expect additional fields to generate a username.
            # roll_number = extra_fields.pop('roll_number', None)
            # grade_obj = extra_fields.pop('grade', None)
            # division_obj = extra_fields.pop('division', None)
            # if not roll_number:
            #     raise ValueError("roll_number must be provided for student user creation")
            # grade_str = (grade_obj.name if hasattr(grade_obj, 'name') else str(grade_obj)).replace(" ", "") if grade_obj else ""
            # division_str = (division_obj.name if hasattr(division_obj, 'name') else str(division_obj)).replace(" ", "") if division_obj else ""
            # if not UserName:
            #     UserName = f"s{roll_number}{grade_str}{division_str}"
    else:
        # For admin/teacher users, generate a sequential username if not provided.
        if user:
            # Use a prefix based on the user_type.
            prefix_map = {'Admin': 'A', 'Teacher': 'F'}
            prefix = prefix_map.get(user_type, 'S')
            count = User.objects.all().count()
            UserName = f"{prefix}{count + 1:03d}"
    return UserName