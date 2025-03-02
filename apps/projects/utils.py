def get_teacher_for_grade_division(grade, division):
    """
    Returns the first teacher found who is assigned to the given grade and division.
    Adjust the logic as needed.
    """
    from apps.accounts.models.user import User  # import your User model
    # Assumes that the teacher's role is 'teacher' and that their details are linked via a OneToOneField.
    teacher = User.objects.filter(
        details__UserType='Teacher',
        details__GradeId=grade,
        details__DivisionId=division
    ).first()
    return teacher