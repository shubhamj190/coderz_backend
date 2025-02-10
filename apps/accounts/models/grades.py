from django.db import models

class Grade(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Grade 2"
    description = models.TextField(null=True, blank=True)

class Division(models.Model):
    grade = models.ForeignKey('accounts.Grade', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # e.g., "A", "B", "C"