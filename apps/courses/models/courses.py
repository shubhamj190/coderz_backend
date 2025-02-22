from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    programming_language = models.CharField(max_length=100)  # e.g., Python, Scratch
    difficulty_level = models.CharField(
        max_length=20
    )  # Beginner, Intermediate, Advanced
    grade = models.ForeignKey("accounts.Grade", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LessonPlan(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField()  # in minutes
    order = models.IntegerField()  # for sequencing lessons
    created_at = models.DateTimeField(auto_now_add=True)


class LearningContent(models.Model):
    lesson_plan = models.ForeignKey("LessonPlan", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50)  # video, pdf, ppt, ebook
    file = models.FileField(upload_to="learning_content/")
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class StudentCourseEnrollment(models.Model):
    student = models.ForeignKey("accounts.UserDetails", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_status = models.CharField(
        max_length=20,
        choices=[
            ("enrolled", "Enrolled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
    )
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ["student", "course"]
