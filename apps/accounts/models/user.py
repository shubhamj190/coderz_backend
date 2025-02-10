from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager

from apps.accounts.models.grades import Division, Grade

class CustomUserManager(BaseUserManager):
    def create_user(self, UserName=None, Email=None, password=None, role='student', **extra_fields):
        if not Email:
            raise ValueError("The Email must be set")
        
        Email = self.normalize_email(Email)
        
        # If no username is provided, generate one dynamically based on role.
        if not UserName:
            prefix_map = {
                'admin': 'A',
                'teacher': 'F',
                'student': 'S'
            }
            prefix = prefix_map.get(role, 'S')
            # Count existing users with the same role to generate a sequential number.
            count = self.filter(role=role).count()
            # Format the number as three digits (001, 002, etc.)
            UserName = f"{prefix}{count + 1:03d}"
        
        # Create and save the user.
        user = self.model(UserName=UserName, Email=Email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, UserName, Email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(UserName, Email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    UserId = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=50, default='', blank=True, null=True)
    LastName = models.CharField(max_length=50, default='', blank=True, null=True)
    UserName = models.CharField(max_length=150, unique=True)
    NormalizedUserName = models.CharField(max_length=150, unique=True, blank=True)
    Email = models.EmailField(unique=True)
    NormalizedEmail = models.EmailField(unique=True, blank=True)
    EmailConfirmed = models.BooleanField(default=False)
    PhoneNumber = models.CharField(max_length=15, blank=True, null=True)
    AltPhoneNumber = models.CharField(max_length=15, blank=True, null=True)
    PhoneNumberConfirmed = models.BooleanField(default=False)
    TwoFactorEnabled = models.BooleanField(default=False)
    LockoutEnd = models.DateTimeField(null=True, blank=True)
    LockoutEnabled = models.BooleanField(default=True)
    AccessFailedCount = models.IntegerField(default=0)
    InstitutionId = models.IntegerField(null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='')

    USERNAME_FIELD = 'UserName'
    REQUIRED_FIELDS = ['Email']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.NormalizedUserName = self.UserName.lower()
        self.NormalizedEmail = self.Email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.UserName} ({self.role})"

    @property
    def id(self):
        return self.UserId

    class Meta:
        db_table = 'usersidentity'


class Teacher(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='teacher_profile')
    FirstName = models.CharField(max_length=50, default='', blank=True, null=True)
    LastName = models.CharField(max_length=50, default='', blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)  # e.g., Python, Scratch, Web Development
    qualification = models.CharField(max_length=255)
    years_of_experience = models.IntegerField()
    assigned_grades = models.ManyToManyField(Grade, related_name='teachers')
    assigned_divisions = models.ManyToManyField(Division, related_name='teachers')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"