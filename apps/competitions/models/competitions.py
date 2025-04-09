from django.db import models 

class Competition(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    competition_type = models.CharField(max_length=50)  # school, zonal, national
    grade_level = models.ForeignKey('accounts.Grade', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CompetitionSubmission(models.Model):
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE)
    student = models.ForeignKey('accounts.UsersIdentity', on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='competition_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    ranking = models.IntegerField(null=True)