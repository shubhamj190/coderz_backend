from django.db import models

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)  # system, manual
    target_audience = models.CharField(max_length=50)  # all, teachers, students
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey('accounts.UsersIdentity', related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey('accounts.UsersIdentity', related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)