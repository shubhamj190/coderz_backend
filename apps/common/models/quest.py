from django.db import models
from apps.common.models.institution import Institutions, Board


# Create your models here.
class QuestLabel(models.Model):
    Id = models.AutoField(primary_key=True, db_column="Id")
    label = models.CharField(max_length=50, null=True, blank=True, db_column="label")
    BGColor = models.CharField(
        max_length=50, null=True, blank=True, db_column="BGColor"
    )
    IsActive = models.BooleanField(null=True, blank=True, db_column="IsActive")

    class Meta:
        db_table = "QuestLabel"
        managed = False


class Quest(models.Model):
    QId = models.AutoField(primary_key=True, db_column="QId")
    QuestId = models.CharField(
        max_length=50, null=True, unique=True, blank=True, db_column="QuestId"
    )
    QuestName = models.CharField(
        max_length=100, null=True, blank=True, db_column="QuestName"
    )
    QuestDisplayName = models.CharField(
        max_length=100, null=True, blank=True, db_column="QuestDisplayName"
    )
    QuestDescription = models.TextField(
        null=True, blank=True, db_column="QuestDescription"
    )
    SequenceNo = models.IntegerField(null=False, db_column="SequenceNo")
    IsFree = models.BooleanField(null=True, blank=True, db_column="IsFree")
    FreeDuration = models.IntegerField(null=True, blank=True, db_column="FreeDuration")
    Duration = models.IntegerField(null=True, blank=True, db_column="Duration")
    InstitutionId = models.ForeignKey(
        Institutions,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="InstitutionId",
        related_name="quest_institution",
    )
    QuestPrice = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, db_column="QuestPrice"
    )
    Currency = models.CharField(
        max_length=50, null=True, blank=True, db_column="Currency"
    )
    BoardId = models.ForeignKey(
        Board,
        to_field="BoardId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="BoardId",
        related_name="quest_board",
    )
    Standard = models.CharField(
        max_length=100, null=True, blank=True, db_column="Standard"
    )
    DBPath = models.CharField(max_length=250, null=True, blank=True, db_column="DBPath")
    IsActive = models.BooleanField(null=False, db_column="IsActive")
    IsDeleted = models.BooleanField(null=False, db_column="IsDeleted")
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    DBGeneratedDate = models.DateTimeField(
        null=True, blank=True, db_column="DBGeneratedDate"
    )
    IsAcademic = models.BooleanField(null=True, blank=True, db_column="IsAcademic")
    CategoryId = models.IntegerField(null=True, blank=True, db_column="CategoryId")
    QuestVideo = models.CharField(
        max_length=1000, null=True, blank=True, db_column="QuestVideo"
    )
    QuestIcon = models.CharField(
        max_length=1000, null=True, blank=True, db_column="QuestIcon"
    )
    Tagalue = models.CharField(
        max_length=50, null=True, blank=True, db_column="Tagalue"
    )
    TagColor = models.CharField(
        max_length=50, null=True, blank=True, db_column="TagColor"
    )
    DiscountType = models.CharField(
        max_length=2, null=True, blank=True, db_column="DiscountType"
    )
    Discount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, db_column="Discount"
    )
    DiscountValidFrom = models.DateTimeField(
        null=True, blank=True, db_column="DiscountValidFrom"
    )
    DiscountValidTill = models.DateTimeField(
        null=True, blank=True, db_column="DiscountValidTill"
    )
    QuestLabelId = models.ForeignKey(
        QuestLabel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="QuestLabelId",
        related_name="quest_board",
    )
    IsOnline = models.BooleanField(null=True, blank=True, db_column="IsOnline")
    FormUrl = models.CharField(
        max_length=500, null=True, blank=True, db_column="FormUrl"
    )
    GradeIds = models.CharField(
        max_length=1024, null=True, blank=True, db_column="GradeIds"
    )
    IsNexool = models.BooleanField(default=False, db_column="IsNexool")
    RefQuestId = models.CharField(
        max_length=50, null=True, blank=True, db_column="RefQuestId"
    )
    MigrateBy = models.CharField(
        max_length=50, null=True, blank=True, db_column="MigrateBy"
    )
    MigrateOn = models.DateTimeField(null=True, blank=True, db_column="MigrateOn")

    class Meta:
        db_table = "Quest"
        managed = False
