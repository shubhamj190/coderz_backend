import os
from django.db import models

from apps.accounts.models.grades import Division, Grade
from apps.accounts.models.user import User

class ClassroomProject(models.Model):
    title = models.CharField(max_length=255)  # e.g., “Odd-Even Number”
    description = models.TextField(blank=True, null=True)
    grade = models.ForeignKey("accounts.Grade", on_delete=models.CASCADE, related_name="projects")
    division = models.ForeignKey("accounts.Division", on_delete=models.CASCADE, related_name="projects")
    group = models.ForeignKey("accounts.GroupMaster", on_delete=models.CASCADE, related_name="projects")
    assigned_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_projects"
    )
    # Thumbnail for project
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)

    # Meta fields
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (Grade: {self.grade.GradeName}, Division: {self.division.DivisionName})"

    class Meta:
        db_table = "ClassroomProject"
        managed = False

class ProjectAsset(models.Model):
    """
    Stores different types of assets (images, videos, PDFs, PPTs, etc.)
    related to a ClassroomProject.
    """
    project = models.ForeignKey(ClassroomProject, on_delete=models.CASCADE, related_name="assets")
    file = models.FileField(upload_to="projects/assets/")
    file_type = models.CharField(
        max_length=10,
        choices=[
            ("image", "Image"),
            ("video", "Video"),
            ("pdf", "PDF"),
            ("ppt", "PowerPoint"),
            ("doc", "Document"),
            ("other", "Other"),
        ],
        default="other",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asset for {self.project.title} ({self.file_type})"
    class Meta:
        db_table = "ProjectAsset"


class ReflectiveQuiz(models.Model):
    """
    Reflective quizzes associated with a ClassroomProject.
    """
    project = models.ForeignKey(ClassroomProject, on_delete=models.CASCADE, related_name="quizzes")
    question = models.TextField()
    options = models.JSONField(help_text="Store options as a dictionary, e.g. {'1': 'A', '2': 'B', '3': 'C'}")
    answers = models.JSONField(help_text="Store correct answer indices as a list, e.g. [1, 3]")
    multiselect = models.BooleanField(default=False, help_text="Whether multiple answers can be selected")

    def __str__(self):
        return f"Quiz for {self.project.title}: {self.question[:50]}..."
    
    class Meta:
        db_table = 'ReflectiveQuiz'
        managed = False

class ProjectSession(models.Model):
    project = models.ForeignKey(ClassroomProject, on_delete=models.CASCADE, related_name="sessions")
    title = models.CharField(max_length=255)   # e.g. “Session 01”
    overview_text = models.TextField(blank=True, null=True)
    ppt_file = models.FileField(upload_to="projects/sessions/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True, null=True)
    # You can add more fields for session content, videos, attachments, etc.

    # If you have a concept of “Module” or “Module Name” (e.g., “VS-Code”), add it:
    module_name = models.CharField(max_length=100, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def file_type(self):
        if self.ppt_file:
            return os.path.splitext(self.ppt_file.name)[-1].lower().replace(".", "")
        return None

    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    class Meta:
        db_table = 'ProjectSession'
        managed = False

class ProjectSubmission(models.Model):
    project = models.ForeignKey(
        'ClassroomProject', 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    student = models.ForeignKey(
        'accounts.UserDetails', 
        on_delete=models.CASCADE, 
        related_name='project_submissions'
    )
    submission_file = models.FileField(
        upload_to='project_submissions/', 
        blank=True, 
        null=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    teacher_evaluation = models.TextField(blank=True, null=True)
    marks_obtained = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"{self.student.FirstName} {self.student.LastName} - {self.project.title}"
    
    class Meta:
        db_table = 'ProjectSubmission'
        managed = False

class ReflectiveQuizSubmission(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="quiz_submissions",
        db_column="StudentId"
    )
    quiz = models.ForeignKey(
        ReflectiveQuiz, 
        on_delete=models.CASCADE,
        related_name="submissions",
        db_column="QuizId"
    )
    selected_options = models.JSONField(
        db_column="SelectedOptions",
        help_text="Store selected options as a list, e.g., [1, 3]"
    )
    is_correct = models.BooleanField(db_column="IsCorrect")
    submitted_at = models.DateTimeField(auto_now_add=True, db_column="SubmittedAt")

    def __str__(self):
        return f"{self.student.FirstName} {self.student.LastName} - Quiz {self.quiz.id}"

    class Meta:
        db_table = 'ReflectiveQuizSubmission'
        managed = True
