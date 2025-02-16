from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    project_type = models.CharField(max_length=50)  # classroom, personalized
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProjectSubmission(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    student = models.ForeignKey('User', on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='project_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # submitted, evaluated
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    feedback = models.TextField(null=True)