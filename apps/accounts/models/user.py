from __future__ import unicode_literals
from django.db import models
from apps.common.models.location import Location
from apps.common.models.institution import ClassMaster, SubClassMaster
from apps.common.models.quest import Quest
from apps.common.models.mission import Mission
from apps.common.models.operation import Operation, Task, SubTask
from apps.common.models.institution import Institutions
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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


class UserQuest(models.Model):
    UserQuestId = models.AutoField(primary_key=True)
    UserId = models.CharField(max_length=255)
    QuestId = models.CharField(max_length=255)
    IsFree = models.BooleanField(blank=True, null=True)
    StartDate = models.DateTimeField(blank=True, null=True)
    EndDate = models.DateTimeField(blank=True, null=True)
    ModifiedOn = models.DateTimeField(blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    ImportCode = models.CharField(max_length=255, blank=True, null=True)
    PgOrderId = models.CharField(max_length=255, blank=True, null=True)
    ProductId = models.CharField(max_length=255, blank=True, null=True)
    MissionList = models.TextField(blank=True, null=True)
    QID= models.ForeignKey(
        Quest,
        to_field="QId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="QID",
        related_name="UserQuest_Qid"
    )

    def __str__(self):
        return f"UserQuest - UserQuestId: {self.UserQuestId}, UserId: {self.UserId}, QuestId: {self.QuestId}"

    class Meta:
        db_table = "UserQuest"
        managed = False


class UplaodRegistry(models.Model):
    id = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(
        UsersIdentity, on_delete=models.CASCADE, db_column="UserId"
    )
    teacher_id = models.IntegerField(null=True, default=None)
    url = models.TextField(max_length=255)
    remarks = models.CharField(max_length=50)

    class Meta:
        db_table = "UploadRegistry"
        managed = False


class Tokens(models.Model):
    id = models.AutoField(primary_key=True, db_column="TokenId")
    UserId = models.ForeignKey(
        UsersIdentity,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        db_column="UserId",
        related_name="tokens",
    )
    DeviceId = models.CharField(
        max_length=50, null=True, blank=True, db_column="DeviceId"
    )
    AppId = models.CharField(max_length=30, null=True, blank=True, db_column="AppId")
    AuthToken = models.CharField(
        max_length=250, null=False, blank=False, db_column="AuthToken"
    )
    IssuedOn = models.DateTimeField()
    ExpiresOn = models.DateTimeField()

    class Meta:
        db_table = "Tokens"
        managed = False


class GroupMaster(models.Model):
    GID = models.AutoField(primary_key=True, db_column="GID")
    GroupId = models.CharField(
        max_length=100, unique=True, null=True, blank=True, db_column="GroupId"
    )
    GroupName = models.CharField(
        max_length=255, null=False, blank=False, db_column="GroupName"
    )
    GroupShortName = models.CharField(
        max_length=255, null=True, blank=True, db_column="GroupShortName"
    )
    LocationId = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        db_column="LocationId",
        related_name="group_mater_location",
    )
    QuestId = models.CharField(
        max_length=50, null=True, blank=True, db_column="QuestId"
    )
    IsActive = models.BooleanField(null=False, db_column="IsActive")
    IsDeleted = models.BooleanField(null=False, db_column="IsDeleted")
    PropertyJSON = models.TextField(null=True, blank=True, db_column="PropertyJSON")
    ClassId = models.ForeignKey(
        ClassMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="ClassId",
        related_name="group_master_class",
    )
    SubClassId = models.ForeignKey(
        SubClassMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="SubClassId",
        related_name="group_master_subclass",
    )
    SequenceNo = models.IntegerField(null=True, blank=True, db_column="SequenceNo")
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")

    class Meta:
        db_table = "GroupMaster"
        managed = False


class GroupQuestDetails(models.Model):
    GroupQuestId = models.AutoField(primary_key=True, db_column="GroupQuestId")
    LocationId = models.ForeignKey(
        Location,
        to_field="LocationId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="LocationId",
        related_name="group_quest_details_location",
    )
    GroupId = models.ForeignKey(
        GroupMaster,
        to_field="GroupId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GroupId",
        related_name="group_quest_details_group",
    )
    QuestId = models.ForeignKey(
        Quest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="QuestId",
        related_name="group_quest_details_quest",
    )
    IsFree = models.BooleanField(null=True, blank=True, db_column="IsFree")
    StartDate = models.DateTimeField(null=True, blank=True, db_column="StartDate")
    EndDate = models.DateTimeField(null=True, blank=True, db_column="EndDate")
    IsDeleted = models.BooleanField(null=False, db_column="IsDeleted")
    ImportCode = models.CharField(
        max_length=50, null=True, blank=True, db_column="ImportCode"
    )
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    ProductId = models.CharField(
        max_length=50, null=True, blank=True, db_column="ProductId"
    )
    MissionList = models.TextField(null=True, blank=True, db_column="MissionList")

    class Meta:
        db_table = "GroupQuestDetails"
        managed = False


class UserGroup(models.Model):
    UserId = models.OneToOneField(
        UsersIdentity,
        primary_key=True,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        related_name="user_group_useridentity",
    )
    LocationId = models.ForeignKey(
        Location,
        to_field="LocationId",
        on_delete=models.DO_NOTHING,
        db_column="LocationId",
        related_name="user_group_locations",
    )
    GroupId = models.ForeignKey(
        GroupMaster,
        to_field="GroupId",
        on_delete=models.DO_NOTHING,
        db_column="GroupId",
        related_name="user_group_group_master",
    )
    ModifiedOn = models.DateTimeField(blank=True, null=True)
    IsDeleted = models.BooleanField(default=False)
    Import_Code = models.CharField(max_length=255, blank=True, null=True)
    LID = models.ForeignKey(
        Location,
        to_field="LID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="LID",
        related_name="user_group_lid",
    )
    GID= models.ForeignKey(
        GroupMaster,
        to_field="GID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GID",
        related_name="user_group_gid",
    )

    class Meta:
        managed = False
        db_table = "UserGroup"
        unique_together = (("UserId", "LocationId", "GroupId", "IsDeleted"),)
        indexes = [
            models.Index(fields=["LocationId", "GroupId"], name="NCI_UG"),
            models.Index(fields=["IsDeleted"], name="NCI_UserGroup_isdelete"),
            models.Index(fields=["LocationId", "IsDeleted"], name="NCI_UserGroup_L_D"),
        ]


class CumulativeReport(models.Model):
    UserId = models.ForeignKey(
        UsersIdentity,
        to_field="UserId",
        on_delete=models.CASCADE,
        db_column="UserId",
        related_name="cumulative_reports_user_identity",
    )
    QuestId = models.ForeignKey(
        Quest,
        to_field="QuestId",
        on_delete=models.CASCADE,
        db_column="QuestId",
        related_name="cumulative_reports_quest",
    )
    Date = models.DateTimeField(db_column="Date")
    MissionId = models.ForeignKey(
        Mission,
        to_field="MissionId",
        on_delete=models.CASCADE,
        db_column="MissionId",
        related_name="cumulative_reports_mission",
    )
    OperationId = models.ForeignKey(
        Operation,
        to_field="OperationId",
        on_delete=models.CASCADE,
        db_column="OperationId",
        related_name="cumulative_reports_operation",
    )
    TaskId = models.ForeignKey(
        Task,
        to_field="TaskId",
        on_delete=models.CASCADE,
        db_column="TaskId",
        related_name="cumulative_reports_task",
    )
    SubTaskId = models.ForeignKey(
        SubTask,
        to_field="SubTaskId",
        on_delete=models.CASCADE,
        db_column="SubTaskId",
        related_name="cumulative_reports_subtask",
    )
    AVCount = models.IntegerField(null=True, blank=True, default=0, db_column="AVCount")
    TestCount = models.IntegerField(
        null=True, blank=True, default=0, db_column="TestCount"
    )
    WebCount = models.IntegerField(
        null=True, blank=True, default=0, db_column="WebCount"
    )
    ActivityCount = models.IntegerField(
        null=True, blank=True, default=0, db_column="ActivityCount"
    )
    DAVCount = models.IntegerField(null=True, blank=True, db_column="DAVCount")
    DTestCount = models.IntegerField(null=True, blank=True, db_column="DTestCount")
    DWebCount = models.IntegerField(null=True, blank=True, db_column="DWebCount")
    DActivityCount = models.IntegerField(
        null=True, blank=True, db_column="DActivityCount"
    )
    TimeSpent = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, db_column="TimeSpent"
    )

    class Meta:
        db_table = "Cumulative_Report"
        managed = (
            False  # Set to False if you do not want Django to manage the table schema
        )
        unique_together = (
            (
                "UserId",
                "QuestId",
                "Date",
                "MissionId",
                "OperationId",
                "TaskId",
                "SubTaskId",
            ),
        )
        indexes = [
            models.Index(fields=["Date"], name="NCI_CR"),
        ]


class TeacherLocationDetails(models.Model):
    mapping_id = models.AutoField(
        primary_key=True, db_column="MappingId"
    )  # MappingId in SQL
    user_id = models.CharField(max_length=50, db_column="UserId")  # UserId in SQL
    institution_id = models.IntegerField(
        db_column="InstitutionId"
    )  # InstitutionId in SQL
    location_id = models.CharField(
        max_length=50, db_column="LocationId"
    )  # LocationId in SQL
    group_id = models.CharField(max_length=50, db_column="GroupId")  # GroupId in SQL
    is_deleted = models.BooleanField(db_column="IsDeleted")  # IsDeleted in SQL
    modified_on = models.DateTimeField(
        null=True, blank=True, db_column="ModifiedOn"
    )  # ModifiedOn in SQL
    class_id = models.IntegerField(
        null=True, blank=True, db_column="ClassId"
    )  # ClassId in SQL
    subclass_id = models.IntegerField(
        null=True, blank=True, db_column="SubClassId"
    )  # SubClassId in SQL
    LID = models.ForeignKey(
        Location,
        to_field="LID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="LID",
        related_name="teacher_location_details_lid",
    )
    GID= models.ForeignKey(
        GroupMaster,
        to_field="GID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GID",
        related_name="teacher_location_details_gid",
    )

    class Meta:
        managed = False
        db_table = "TeacherLocationDetails"  # Specifies the table name in the database
        # indexes = [
        #     models.Index(
        #         fields=["user_id", "is_deleted"],
        #         name="NCI_TeacherLocationDetails_UID_IDel",
        #     )  # Non-clustered index
        # ]
        constraints = [
            models.UniqueConstraint(
                fields=["mapping_id"], name="PK_TeacherLocationMapping"
            )  # Primary key constraint
        ]


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