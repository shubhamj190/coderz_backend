from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager

from apps.accounts.models.grades import Division, Grade

class CustomUserManager(BaseUserManager):
    def create_user(self, UserName=None, Email=None, password=None, role='student', **extra_fields):
        if not Email:
            raise ValueError("The Email must be set")
        
        Email = self.normalize_email(Email)
        
        if role == 'student':
            # Pop the keys that are not part of the User model
            roll_number = extra_fields.pop('roll_number', None)
            grade_obj = extra_fields.pop('grade', None)
            division_obj = extra_fields.pop('division', None)
            
            if not roll_number:
                raise ValueError("roll_number must be provided for student user creation")
            
            # Determine grade and division strings (removing spaces)
            if grade_obj:
                grade_str = grade_obj.name if hasattr(grade_obj, 'name') else str(grade_obj)
                grade_str = grade_str.replace(" ", "")
            else:
                grade_str = ""
                
            if division_obj:
                division_str = division_obj.name if hasattr(division_obj, 'name') else str(division_obj)
                division_str = division_str.replace(" ", "")
            else:
                division_str = ""
            
            # Generate the username based on roll number, grade, and division if not provided.
            if not UserName:
                UserName = f"s{roll_number}{grade_str}{division_str}"
        else:
            # For non-student roles, generate a sequential username if not provided.
            if not UserName:
                prefix_map = {
                    'admin': 'A',
                    'teacher': 'F',
                    'student': 'S'
                }
                prefix = prefix_map.get(role, 'S')
                count = self.filter(role=role).count()
                UserName = f"{prefix}{count + 1:03d}"
        
        # Create and save the user without the student-only extra fields.
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

class Institution(models.Model):
    # Minimal representation for the FK reference; adjust as needed.
    InstitutionId = models.IntegerField(primary_key=True, db_column='InstitutionId')
    # Add other fields if required.

    class Meta:
        db_table = 'Institutions'
        managed = False

    def __str__(self):
        return str(self.InstitutionId)
class User(AbstractBaseUser, PermissionsMixin):
    UserId = models.CharField(primary_key=True, max_length=450, db_column='UserId')
    UserName = models.CharField(max_length=256, unique=True, null=True, blank=True, db_column='UserName')
    NormalizedUserName = models.CharField(max_length=256, unique=True, null=True, blank=True, db_column='NormalizedUserName')
    Email = models.CharField(max_length=256, unique=True, null=True, blank=True, db_column='Email')
    NormalizedEmail = models.CharField(max_length=256, unique=True, null=True, blank=True, db_column='NormalizedEmail')
    EmailConfirmed = models.BooleanField(default=False, db_column='EmailConfirmed')
    PasswordHash = models.TextField(null=True, blank=True, db_column='PasswordHash')
    SecurityStamp = models.TextField(null=True, blank=True, db_column='SecurityStamp')
    ConcurrencyStamp = models.TextField(null=True, blank=True, db_column='ConcurrencyStamp')
    PhoneNumber = models.TextField(null=True, blank=True, db_column='PhoneNumber')
    PhoneNumberConfirmed = models.BooleanField(default=False, db_column='PhoneNumberConfirmed')
    TwoFactorEnabled = models.BooleanField(default=False, db_column='TwoFactorEnabled')
    LockoutEnd = models.DateTimeField(null=True, blank=True, db_column='LockoutEnd')
    LockoutEnabled = models.BooleanField(default=True, db_column='LockoutEnabled')
    AccessFailedCount = models.IntegerField(default=0, db_column='AccessFailedCount')
    InstitutionId = models.ForeignKey(Institution, on_delete=models.CASCADE, db_column='InstitutionId')
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    IsDeleted = models.BooleanField(default=False, db_column='IsDeleted')

    USERNAME_FIELD = 'UserName'
    REQUIRED_FIELDS = ['Email']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.NormalizedUserName = self.UserName.lower()
        self.NormalizedEmail = self.Email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.UserName}"

    @property
    def id(self):
        return self.UserId

    class Meta:
        db_table = 'UserIdentity'
        managed = False  # Use the existing table without migrations

class UserDetails(models.Model):
    # Use a OneToOneField with primary_key=True to share the same primary key as the User table.
    USER_TYPE_CHOICES = [
        ('Learner', 'Learner'),
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='UserId',
        related_name='details'
    )
    ContactNo = models.CharField(max_length=50, blank=True, null=True, db_column='ContactNo')
    AdditionalContactNo = models.CharField(max_length=50, blank=True, null=True, db_column='AdditionalContactNo')
    Address = models.TextField(blank=True, null=True, db_column='Address')
    Location = models.CharField(max_length=100, blank=True, null=True, db_column='Location')
    Pincode = models.CharField(max_length=50, blank=True, null=True, db_column='Pincode')
    CityCode = models.CharField(max_length=50, blank=True, null=True, db_column='CityCode')
    StateCode = models.CharField(max_length=50, blank=True, null=True, db_column='StateCode')
    CountryCode = models.CharField(max_length=10, blank=True, null=True, db_column='CountryCode')
    LastUsedDevice = models.CharField(max_length=50, blank=True, null=True, db_column='LastUsedDevice')
    PromoCode = models.CharField(max_length=10, blank=True, null=True, db_column='PromoCode')
    PromoRefCode = models.CharField(max_length=10, blank=True, null=True, db_column='PromoRefCode')
    ModifiedOn = models.DateTimeField(blank=True, null=True, db_column='ModifiedOn')
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    IsDeleted = models.BooleanField(default=False, db_column='IsDeleted')
    CustomerGST = models.CharField(max_length=500, blank=True, null=True, db_column='CustomerGST')
    UserSource = models.CharField(max_length=50, blank=True, null=True, db_column='UserSource')
    SchoolName = models.CharField(max_length=100, blank=True, null=True, db_column='SchoolName')
    BoardId = models.ForeignKey('accounts.Board', on_delete=models.CASCADE, blank=True, null=True, db_column='BoardID')
    GradeId = models.ForeignKey(Grade, on_delete=models.CASCADE, blank=True, null=True, db_column='GradeId')
    DivisionId = models.ForeignKey(Division, on_delete=models.CASCADE, blank=True, null=True, db_column='DivisionId')
    QuestId = models.CharField(max_length=50, blank=True, null=True, db_column='QuestId')
    UserType = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, blank=True, null=True, db_column='UserType')
    FirstName = models.CharField(max_length=50, blank=True, null=True, db_column='FirstName')
    MiddleName = models.CharField(max_length=50, blank=True, null=True, db_column='MiddleName')
    LastName = models.CharField(max_length=50, blank=True, null=True, db_column='LastName')
    LastQuestAccessed = models.CharField(max_length=50, blank=True, null=True, db_column='LastQuestAccessed')
    IsDirectUser = models.BooleanField(default=False, db_column='IsDirectUser')
    UTMData = models.CharField(max_length=1000, blank=True, null=True, db_column='UTMData')
    AdmissionNo = models.CharField(max_length=500, blank=True, null=True, db_column='AdmissionNo')
    Gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, db_column='Gender')

    class Meta:
        db_table = 'UserDetails'
        managed = False  # Do not manage this table via Django migrations

    def __str__(self):
        return f"Details for {self.user.UserName}"
    
class Location(models.Model):
    LID = models.AutoField(primary_key=True, db_column='LID')
    LocationId = models.CharField(max_length=50, null=True, blank=True, db_column='LocationId')
    LocationName = models.CharField(max_length=100, db_column='LocationName')
    IsActive = models.BooleanField(db_column='IsActive')
    IsDeleted = models.BooleanField(db_column='IsDeleted')
    InstitutionId = models.IntegerField(db_column='InstitutionId')
    DoNotTrack = models.BooleanField(null=True, blank=True, db_column='DoNotTrack')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsErpUsed = models.BooleanField(null=True, blank=True, db_column='IsErpUsed')
    ERP_API_Url = models.TextField(null=True, blank=True, db_column='ERP_API_Url')
    # Add additional fields if needed

    class Meta:
        db_table = 'Location'
        managed = False

    def save(self, *args, **kwargs):
        self.LocationId = self.LID
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.LID)


class GroupMaster(models.Model):
    GID = models.AutoField(primary_key=True, db_column='GID')
    GroupId = models.CharField(max_length=100, null=True, blank=True, db_column='GroupId')
    GroupName = models.CharField(max_length=255, db_column='GroupName')
    GroupShortName = models.CharField(max_length=255, null=True, blank=True, db_column='GroupShortName')
    LocationId = models.IntegerField(db_column='LocationId')
    QuestId = models.CharField(max_length=50, null=True, blank=True, db_column='QuestId')
    IsActive = models.BooleanField(db_column='IsActive')
    IsDeleted = models.BooleanField(default=False, db_column='IsDeleted')
    PropertyJSON = models.TextField(null=True, blank=True, db_column='PropertyJSON')
    ClassId = models.IntegerField(null=True, blank=True, db_column='ClassId')
    SubClassId = models.IntegerField(null=True, blank=True, db_column='SubClassId')
    SequenceNo = models.IntegerField(null=True, blank=True, db_column='SequenceNo')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    # Add additional fields if needed

    class Meta:
        db_table = 'GroupMaster'
        managed = False

    def save(self, *args, **kwargs):
        self.GroupId = self.GID
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.GID)


class UserGroup(models.Model):
    """
    Represents the user group membership from the UserGroup table.
    The composite key is enforced using unique_together on:
    (UserId, LocationId, GroupId, IsDeleted)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='UserId',
        related_name='user_groups'
    )
    LocationId = models.CharField(max_length=50, db_column='LocationId')
    GroupId = models.CharField(max_length=50, db_column='GroupId')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsDeleted = models.BooleanField(default=False, db_column='IsDeleted')
    Import_Code = models.CharField(max_length=50, null=True, blank=True, db_column='Import_Code')
    LID = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='LID'
    )
    GID = models.ForeignKey(
        GroupMaster,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='GID'
    )

    def save(self, *args, **kwargs):
        self.LocationId = self.LID.LocationId
        self.GroupId = self.GID.GroupId
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'UserGroup'
        managed = False  # Tells Django not to manage (create/modify) this existing table.
        unique_together = (('user', 'LocationId', 'GroupId', 'IsDeleted'),)
        verbose_name = "User Group"
        verbose_name_plural = "User Groups"

    def __str__(self):
        return f"{self.user.UserName} | {self.LocationId} | {self.GroupId} | Deleted: {self.IsDeleted}"