from django.db import models

class Assessment(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=50)  # quiz, test
    duration = models.IntegerField()  # in minutes
    total_marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)  # MCQ, image-based
    marks = models.IntegerField()
    order = models.IntegerField()

class QuestionOption(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)