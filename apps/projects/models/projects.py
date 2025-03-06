import os
from django.db import models

from apps.accounts.models.grades import Division, Grade
from apps.accounts.models.user import User

class ClassroomProject(models.Model):
    title = models.CharField(max_length=255)         # e.g. “Odd-Even Number”
    description = models.TextField(blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="projects")
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="projects")
    assigned_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_projects"
    )
    # If you want an overall image or icon for the project card:
    thumbnail = models.ImageField(upload_to="projects/thumbnails/", blank=True, null=True)

    # Additional meta fields
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} (Grade: {self.grade.GradeName}, Division: {self.division.DivisionName})"
    
    class Meta:
        db_table = 'ClassroomProject'
        managed = False
    

class ProjectSession(models.Model):
    project = models.ForeignKey(ClassroomProject, on_delete=models.CASCADE, related_name="sessions")
    title = models.CharField(max_length=255)   # e.g. “Session 01”
    overview_text = models.TextField(blank=True, null=True)
    ppt_file = models.FileField(upload_to="projects/sessions/", blank=True, null=True)
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