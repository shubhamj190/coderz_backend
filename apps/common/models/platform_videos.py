from django.db import models
from django.conf import settings

class PlatformVideo(models.Model):
    AUDIENCE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('all', 'All'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    # File will be stored in a folder 'videos/' under your configured storage backend
    video_file = models.FileField(upload_to='videos/')
    # Assuming your custom user model is set as the AUTH_USER_MODEL in settings.
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_videos')
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
