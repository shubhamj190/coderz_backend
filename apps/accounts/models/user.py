import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from apps.accounts.models.grades import Division, Grade

class CustomUserManager(BaseUserManager):
    def create_user(self, UserName=None, Email=None, password=None, **extra_fields):
        """
        Create and return a user without storing user type in this table.
        Instead, expect that a 'user_type' is provided in extra_fields,
        and use that for username generation for students.
        """
        if not Email:
            raise ValueError("The Email must be set")
        Email = self.normalize_email(Email)
        
        # Extract user_type from extra_fields (default to 'student')
        user_type = extra_fields.pop('user_type', 'Learner').lower()
        
        if user_type == 'Learner':
            # For student users, expect additional fields to generate a username.
            roll_number = extra_fields.pop('roll_number', None)
            grade_obj = extra_fields.pop('grade', None)
            division_obj = extra_fields.pop('division', None)
            if not roll_number:
                raise ValueError("roll_number must be provided for student user creation")
            grade_str = (grade_obj.name if hasattr(grade_obj, 'name') else str(grade_obj)).replace(" ", "") if grade_obj else ""
            division_str = (division_obj.name if hasattr(division_obj, 'name') else str(division_obj)).replace(" ", "") if division_obj else ""
            if not UserName:
                UserName = f"s{roll_number}{grade_str}{division_str}"
        else:
            # For admin/teacher users, generate a sequential username if not provided.
            if not UserName:
                # Use a prefix based on the user_type.
                prefix_map = {'admin': 'A', 'teacher': 'F'}
                prefix = prefix_map.get(user_type, 'S')
                count = self.all().count()
                UserName = f"{prefix}{count + 1:03d}"
        
        user = self.model(UserName=UserName, Email=Email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, UserName, Email, password=None, **extra_fields):
        # For superuser, we force user_type to 'admin'.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(UserName, Email, password, **extra_fields)

class Institutions(models.Model):
    InstitutionId = models.AutoField(primary_key=True, db_column="InstitutionId")
    InstitutionName = models.CharField(max_length=100, db_column="InstitutionName")
    EmailId = models.CharField(max_length=200, db_column="EmailId")
    PhoneNo = models.CharField(max_length=50, null=True, blank=True, db_column="PhoneNo")
    Address = models.CharField(max_length=200, null=True, blank=True, db_column="Address")
    City = models.CharField(max_length=50, null=True, blank=True, db_column="City")
    State = models.CharField(max_length=50, null=True, blank=True, db_column="State")
    Country = models.CharField(max_length=100, null=True, blank=True, db_column="Country")
    Pin = models.CharField(max_length=15, null=True, blank=True, db_column="Pin")
    Logopath = models.CharField(max_length=150, db_column="Logopath")  # Assuming it's a file path
    ConfigJson = models.JSONField(null=True, blank=True, db_column="ConfigJson")  # Storing JSON data
    ValidityEndDate = models.DateTimeField(null=True, blank=True, db_column="ValidityEndDate")
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    IsActive = models.BooleanField(default=True, db_column="IsActive")
    IsDeleted = models.BooleanField(default=False, db_column="IsDeleted")

    class Meta:
        db_table = "Institutions"
        managed = False  # Set to False if this table already exists in MSSQL
        ordering = ["InstitutionName"]

    def __str__(self):
        return self.InstitutionName
class User(AbstractBaseUser, PermissionsMixin):
    UserId = models.CharField(max_length=256, primary_key=True, default=uuid.uuid4, editable=False, db_column='UserId')
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
    InstitutionId = models.IntegerField(default=0, db_column='InstitutionId')
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    IsDeleted = models.BooleanField(default=False, db_column='IsDeleted')

    # We want to override the inherited "password" field.
    password = None  # This hides the default "password" field from AbstractBaseUser.

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
    
    # Define the password property to use PasswordHash
    @property
    def password(self):
        return self.PasswordHash

    @password.setter
    def password(self, raw_password):
        self.set_password(raw_password)

    def set_password(self, raw_password):
        self.PasswordHash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.PasswordHash)
    
    @property
    def role(self):
        return self.details.UserType

    class Meta:
        db_table = 'UsersIdentity'
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
    GradeId = models.CharField(max_length=50, blank=True, null=True, db_column='GradeId')
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
    date_of_birth = models.DateField(null=True, blank=True, db_column='date_of_birth')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True, db_column='ProfilePic')

    class Meta:
        db_table = 'UserDetails'
        # managed = False  # Do not manage this table via Django migrations

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
        self.GroupId = f"G{self.GID}"
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.GID)

# this is specific for students
class UserGroup(models.Model):
    """
    Represents the user group membership from the UserGroup table.
    The composite key is enforced using unique_together on:
    (UserId, LocationId, GroupId, IsDeleted)
    """
    # Disable Django's auto-generated primary key.
    id = None
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
    
class TeacherLocationDetails(models.Model):
    MappingId = models.AutoField(primary_key=True, db_column="MappingId")
    UserId = models.CharField(max_length=50, db_column="UserId")
    InstitutionId = models.IntegerField(db_column="InstitutionId")
    LocationId = models.CharField(max_length=50, db_column="LocationId")
    GroupId = models.CharField(max_length=50, db_column="GroupId")
    IsDeleted = models.BooleanField(default=False, db_column="IsDeleted")
    ModifiedOn = models.DateTimeField(auto_now=True,null=True, blank=True, db_column="ModifiedOn")
    ClassId = models.IntegerField(null=True, blank=True, db_column="ClassId")
    SubClassId = models.IntegerField(null=True, blank=True, db_column="SubClassId")
    LID = models.ForeignKey(
        Location, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        db_column="LID"
    )
    GID = models.ForeignKey(
        GroupMaster, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        db_column="GID"
    )

    class Meta:
        db_table = "TeacherLocationDetails"
        managed = False  # Prevents Django from modifying the existing MSSQL table

    def __str__(self):
        return f"Mapping {self.MappingId} - User {self.UserId}"