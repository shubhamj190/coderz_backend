from apps.accounts.models.user import UsersIdentity, UserDetails
def user_name_creator(user_type, user):
    UserName = None
    if user_type == 'Learner':
        if user:
            grade_obj=user.details.GradeId
            # division_obj=user.details.DivisionId

            # For student users, expect additional fields to generate a username.
            roll_number = UserDetails.objects.filter(GradeId=grade_obj).count() + 1
            if not roll_number:
                raise ValueError("roll_number must be provided for student user creation")
            grade_str = (grade_obj.GradeId if hasattr(grade_obj, 'GradeId') else str(grade_obj)).replace(" ", "") if grade_obj else ""
            # division_str = (division_obj.DivisionName if hasattr(division_obj, 'DivisionName') else str(division_obj)).replace(" ", "") if division_obj else ""
            if not UserName:
                UserName = f"L{roll_number}{grade_str}"
    else:
        # For admin/teacher users, generate a sequential username if not provided.
        if user:
            # Use a prefix based on the user_type.
            prefix_map = {'Admin': 'A', 'Teacher': 'F'}
            prefix = prefix_map.get(user_type, 'S')
            count = UsersIdentity.objects.all().count()
            UserName = f"{prefix}{count + 1:03d}"
    return UserName