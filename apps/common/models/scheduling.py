# schedules/models.py

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.accounts.models.user import UserDetails  # Adjust import paths as needed
from apps.accounts.models.grades import Grade, Division  # Adjust import paths as needed
from apps.courses.models.courses import Course  # Adjust import path as needed

class TimeSlot(models.Model):
    """
    Represents a fixed time slot that can be used in schedules.
    This model stores the possible time periods for classes.
    """
    start_time = models.TimeField()
    end_time = models.TimeField()
    display_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = (('start_time', 'end_time'),)
        ordering = ['start_time']

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(_("End time must be after start time."))

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name


class WeekDay(models.Model):
    """
    Represents days of the week.
    """
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    name = models.CharField(max_length=10, choices=DAYS, unique=True)
    order = models.IntegerField(unique=True)  # Ensures correct day order

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """
    Represents the master schedule template for a grade and section within an academic year.
    Optionally includes effective start and end dates to allow schedule changes during the semester.
    """
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    section = models.ForeignKey(Division, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)  # e.g., "2024-2025"
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['grade', 'section', 'academic_year']
        ordering = ['grade', 'section']

    def clean(self):
        if self.effective_start_date and self.effective_end_date:
            if self.effective_end_date < self.effective_start_date:
                raise ValidationError(_("Effective end date must be after start date."))

    def __str__(self):
        return f"{self.grade} {self.section} Schedule - {self.academic_year}"


class ScheduleSlot(models.Model):
    """
    Represents an individual class slot in the schedule.
    Connects the schedule, day, time, course, and teacher.
    """
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='slots')
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(UserDetails, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['schedule', 'day', 'time_slot']
        ordering = ['day__order', 'time_slot__start_time']

    def clean(self):
        # Validate that the teacher is assigned to the schedule's grade and section.
        if self.teacher:
            if self.schedule.grade not in self.teacher.assigned_grades.all():
                raise ValidationError(_("Teacher is not assigned to the schedule's grade."))
            if self.schedule.section not in self.teacher.assigned_divisions.all():
                raise ValidationError(_("Teacher is not assigned to the schedule's section."))
        # Optionally, you could also check if the course is suitable for the given grade/section.

    def __str__(self):
        return f"{self.day} {self.time_slot}: {self.course}"
