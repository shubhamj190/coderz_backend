from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, UserName, Email, password=None, **extra_fields):
        if not Email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(Email)
        user = self.model(
            UserName=UserName,
            Email=email,
            **extra_fields
        )
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

    # From usersidentity table
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=150, unique=True)
    NormalizedUserName = models.CharField(max_length=150, unique=True, blank=True)
    Email = models.EmailField(unique=True)
    NormalizedEmail = models.EmailField(unique=True, blank=True)
    EmailConfirmed = models.BooleanField(default=False)
    PhoneNumber = models.CharField(max_length=15, blank=True, null=True)
    PhoneNumberConfirmed = models.BooleanField(default=False)
    TwoFactorEnabled = models.BooleanField(default=False)
    LockoutEnd = models.DateTimeField(null=True, blank=True)
    LockoutEnabled = models.BooleanField(default=True)
    AccessFailedCount = models.IntegerField(default=0)
    InstitutionId = models.IntegerField(null=True, blank=True)
    IsDeleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Role field for quick access (denormalized from UserDetails)
    role = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

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