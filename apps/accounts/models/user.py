import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from apps.accounts.models.grades import Division, Grade
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

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
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn",auto_now=True)
    IsActive = models.BooleanField(default=True, db_column="IsActive")
    IsDeleted = models.BooleanField(default=False, db_column="IsDeleted")

    class Meta:
        db_table = "Institutions"
        managed = False  # Set to False if this table already exists in MSSQL
        ordering = ["InstitutionName"]

    def __str__(self):
        return self.InstitutionName
class UserMaster(AbstractUser):
    UUID = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    NormalizedUserName = models.CharField(
        max_length=255, db_column="NormalizedUserName"
    )
    NormalizedEmail = models.EmailField(max_length=255, db_column="NormalizedEmail")
    EmailConfirmed = models.BooleanField(default=False, db_column="EmailConfirmed")
    PhoneNumberConfirmed = models.BooleanField(
        default=False, db_column="PhoneNumberConfirmed"
    )
    TwoFactorEnabled = models.BooleanField(default=False, db_column="TwoFactorEnabled")
    LockoutEnd = models.DateTimeField(blank=True, null=True, db_column="LockoutEnd")
    LockoutEnabled = models.BooleanField(default=False, db_column="LockoutEnabled")
    AccessFailedCount = models.IntegerField(default=0, db_column="AccessFailedCount")
    # InstitutionId = models.IntegerField()
    InstitutionId = models.ForeignKey(
        Institutions,
        to_field="InstitutionId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="InstitutionId",
        related_name="UserMaster_Institution",
    )
    IsActive = models.BooleanField(default=False, blank=True, null=True)
    IsDeleted = models.BooleanField(default=False, blank=True, null=True)

    def softdelete(self, *args, **kwargs):
        self.IsDeleted = True
        self.save()

    # Optionally, create a method to restore a soft-deleted user
    def restore(self):
        self.IsDeleted = False
        self.save()
    class Meta:
        db_table = "Users_usermaster" 


# Create your models here.
class UsersIdentity(models.Model):
    UserId = models.CharField(primary_key=True, max_length=255, db_column="UserId")
    UserName = models.CharField(max_length=255, unique=True, db_column="UserName")
    NormalizedUserName = models.CharField(
        max_length=255, db_column="NormalizedUserName"
    )
    Email = models.EmailField(max_length=255, db_column="Email")
    NormalizedEmail = models.EmailField(max_length=255, db_column="NormalizedEmail")
    EmailConfirmed = models.BooleanField(default=False, db_column="EmailConfirmed")
    PasswordHash = models.CharField(max_length=255, db_column="PasswordHash")
    SecurityStamp = models.CharField(max_length=255, db_column="SecurityStamp")
    ConcurrencyStamp = models.CharField(max_length=255, db_column="ConcurrencyStamp")
    PhoneNumber = models.CharField(
        max_length=20, blank=True, null=True, db_column="PhoneNumber"
    )
    PhoneNumberConfirmed = models.BooleanField(
        default=False, db_column="PhoneNumberConfirmed"
    )
    TwoFactorEnabled = models.BooleanField(default=False, db_column="TwoFactorEnabled")
    LockoutEnd = models.DateTimeField(blank=True, null=True, db_column="LockoutEnd")
    LockoutEnabled = models.BooleanField(default=False, db_column="LockoutEnabled")
    AccessFailedCount = models.IntegerField(default=0, db_column="AccessFailedCount")
    # InstitutionId = models.IntegerField()
    InstitutionId = models.ForeignKey(
        Institutions,
        to_field="InstitutionId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="InstitutionId",
        related_name="userlocation",
    )
    IsActive = models.BooleanField(default=False, blank=True, null=True)
    IsDeleted = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.UserName  # or any other meaningful representation

    class Meta:
        db_table = "UsersIdentity"
        managed = False


class UserDetails(models.Model):
    UserId = models.OneToOneField(
        UsersIdentity,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_column="UserId",
        primary_key=True,
        related_name="reverse_UserDetails_Users_Identity",
    )
    ContactNo = models.CharField(max_length=50, blank=True, null=True)
    AdditionalContactNo = models.CharField(max_length=50, blank=True, null=True)
    Address = models.TextField(blank=True, null=True)
    Location = models.CharField(max_length=100, blank=True, null=True)
    Pincode = models.CharField(max_length=50, blank=True, null=True)
    CityCode = models.CharField(max_length=50, blank=True, null=True)
    StateCode = models.CharField(max_length=50, blank=True, null=True)
    CountryCode = models.CharField(max_length=10, blank=True, null=True)
    LastUsedDevice = models.CharField(max_length=50, blank=True, null=True)
    PromoCode = models.CharField(max_length=10, blank=True, null=True)
    PromoRefCode = models.CharField(max_length=10, blank=True, null=True)
    ModifiedOn = models.DateTimeField(blank=True, null=True)
    IsActive = models.BooleanField(default=False)
    IsDeleted = models.BooleanField(default=False)
    CustomerGst = models.CharField(max_length=500, blank=True, null=True)
    UserSource = models.CharField(max_length=50, blank=True, null=True)
    SchoolName = models.CharField(max_length=100, blank=True, null=True)
    BoardId = models.CharField(max_length=50, blank=True, null=True)
    GradeId = models.CharField(max_length=50, blank=True, null=True)
    QuestId = models.CharField(max_length=50, blank=True, null=True)
    UserType = models.CharField(max_length=50, blank=True, null=True)
    FirstName = models.CharField(max_length=50, blank=True, null=True)
    MiddleName = models.CharField(max_length=50, blank=True, null=True)
    LastName = models.CharField(max_length=50, blank=True, null=True)
    LastQuestAccessed = models.CharField(max_length=50, blank=True, null=True)
    IsDirectUser = models.BooleanField(default=False, blank=True, null=True)
    UTMData = models.CharField(max_length=1000, blank=True, null=True)
    AdmissionNo = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"

    class Meta:
        db_table = "UserDetails"
        managed = False
    
class Location(models.Model):
    LID = models.AutoField(primary_key=True, db_column='LID')
    LocationId = models.CharField(max_length=50, null=True, blank=True, db_column='LocationId')
    LocationName = models.CharField(max_length=100, db_column='LocationName')
    IsActive = models.BooleanField(db_column='IsActive')
    IsDeleted = models.BooleanField(db_column='IsDeleted')
    InstitutionId = models.IntegerField(db_column='InstitutionId')
    DoNotTrack = models.BooleanField(null=True, blank=True, db_column='DoNotTrack')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn',auto_now=True)
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
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn',auto_now=True)
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
        UsersIdentity,
        on_delete=models.CASCADE,
        db_column='UserId',
        related_name='user_groups',
        primary_key=True
    )
    LocationId = models.CharField(max_length=50, db_column='LocationId')
    GroupId = models.CharField(max_length=50, db_column='GroupId')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn',auto_now=True)
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
    
class RolesV2(models.Model):
    Id = models.IntegerField(unique=True, db_column="Id")
    RoleId = models.CharField(max_length=450, db_column="RoleId", primary_key=True)
    Name = models.CharField(max_length=256, db_column="Name")
    NormalizedName = models.CharField(max_length=256, db_column="NormalizedName")
    ConcurrencyStamp = models.TextField(db_column="ConcurrencyStamp")
    IsActive = models.BooleanField(db_column="IsActive")
    IsDeleted = models.BooleanField(db_column="IsDeleted")
    CreatedBy = models.CharField(max_length=50)  # Represents VARCHAR(50) for CreatedBy
    CreatedOn = models.DateTimeField(
        default=timezone.now
    )  # Represents DATETIME for CreatedOn
    ModifiedBy = models.CharField(
        max_length=50, null=True, blank=True
    )  # Represents VARCHAR(50) for ModifiedBy
    ModifiedOn = models.DateTimeField(
        null=True, blank=True
    )  # Represents DATETIME for ModifiedOn

    class Meta:
        db_table = "Roles"
        managed = False
        constraints = [
            models.UniqueConstraint(
                fields=["RoleId"], name="UQ_Roles_RoleId"
            )  # Unique constraint on RoleId
        ]

class UserRoles(models.Model):
    UserId = models.ForeignKey(
        UserMaster,
        on_delete=models.CASCADE,
        db_column="UserId",
        default=None,
        related_name="UserRoles_UserId",
    )
    RoleId = models.ForeignKey(
        RolesV2,
        on_delete=models.CASCADE,
        to_field="Id",
        default=None,
        related_name="UserRoles_RoleId",
    )

    class Meta:
        db_table = "UserRoles"
        # managed = False