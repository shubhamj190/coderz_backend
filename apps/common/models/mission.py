from django.db import models
from django.utils import timezone
from apps.common.models.quest import Quest


# Create your models here.
class Mission(models.Model):
    MiId = models.AutoField(primary_key=True, db_column="MiId")
    MissionId = models.CharField(
        max_length=50, unique=True, null=True, blank=True, db_column="MissionId"
    )
    MissionName = models.CharField(
        max_length=200, null=False, blank=False, db_column="MissionName"
    )
    MissionDisplayName = models.CharField(
        max_length=200, null=True, blank=True, db_column="MissionDisplayName"
    )
    SequenceNo = models.IntegerField(null=False, db_column="SequenceNo")
    QuestId = models.ForeignKey(
        Quest,
        to_field="QuestId",
        on_delete=models.CASCADE,
        db_column="QuestId",
        related_name="missions",
    )
    Missionicon = models.CharField(
        max_length=50, null=True, blank=True, db_column="Missionicon"
    )
    Missioniconcolour = models.CharField(
        max_length=50, null=True, blank=True, db_column="Missioniconcolour"
    )
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    IsActive = models.BooleanField(null=False, db_column="IsActive")
    IsDeleted = models.BooleanField(null=False, db_column="IsDeleted")
    MissionB64 = models.TextField(null=True, blank=True, db_column="MissionB64")
    MissionIconName = models.CharField(
        max_length=500, null=True, blank=True, db_column="MissionIconName"
    )
    VideoCount = models.IntegerField(null=True, blank=True, db_column="VideoCount")
    TestCount = models.IntegerField(null=True, blank=True, db_column="TestCount")
    ActivityCount = models.IntegerField(
        null=True, blank=True, db_column="ActivityCount"
    )
    WebContentCount = models.IntegerField(
        null=True, blank=True, db_column="WebContentCount"
    )
    MissionDescription = models.TextField(
        null=True, blank=True, db_column="MissionDescription"
    )
    Points = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, db_column="Points"
    )
    TotalTime = models.CharField(
        max_length=50, null=True, blank=True, db_column="TotalTime"
    )
    IsAcademic = models.BooleanField(default=True, db_column="IsAcademic")
    HasOnlineSession = models.BooleanField(default=False, db_column="HasOnlineSession")
    RefMissionId = models.CharField(
        max_length=50, null=True, blank=True, db_column="RefMissionId"
    )
    MissionIconUrl = models.TextField(null=True, blank=True, db_column="MissionIconUrl")

    class Meta:
        db_table = "Mission"
        managed = (
            False  # Set to False if you do not want Django to manage the table schema
        )
        indexes = [
            models.Index(fields=["IsActive", "IsDeleted"], name="NCI_Mission_IA_ID"),
        ]


class QuestionTypeMaster(models.Model):
    QuestionTypeId = models.AutoField(primary_key=True)
    QuestionTypeCode = models.CharField(max_length=50, null=True, blank=True)
    QuestionTypeName = models.CharField(max_length=250)
    IsParagraphType = models.BooleanField(null=True, blank=True)
    IsActive = models.BooleanField(default=True)
    IsDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "QuestionTypeMaster"


class ParagraphMaster(models.Model):
    ParagraphId = models.AutoField(primary_key=True)
    ParagraphCode = models.CharField(
        max_length=10, editable=False
    )  # Generated in `save()` based on paragraph_id
    ParagraphText = models.TextField()
    ParagraphText_E = models.TextField(null=True, blank=True)
    ModifiedOn = models.DateTimeField(null=True, blank=True)
    IsActive = models.BooleanField(default=True)
    IsDeleted = models.BooleanField(default=False)
    InstitutionId = models.IntegerField(default=1)
    CreatedOn = models.DateTimeField(default=timezone.now)
    CreatedBy = models.CharField(max_length=50, null=True, blank=True)
    ImportCode = models.TextField(null=True, blank=True)
    IsCaseStudy = models.BooleanField(null=True, blank=True)

    # Meta options
    class Meta:
        db_table = "ParagraphMaster"
        ordering = ["ParagraphId"]  # Keep records ordered by ID
        constraints = [
            models.UniqueConstraint(
                fields=["ParagraphCode"], name="unique_paragraph_code"
            )
        ]

    # Auto-generate paragraph_code based on paragraph_id
    def save(self, *args, **kwargs):
        if not self.ParagraphCode and self.ParagraphId:
            self.ParagraphCode = f"PRG{str(self.ParagraphId).zfill(5)}"
        super(ParagraphMaster, self).save(*args, **kwargs)

    # String representation for better readability
    def __str__(self):
        return f'Paragraph {self.ParagraphCode or "New"}'


class MissionQuestion(models.Model):
    MissionQuestionId = models.AutoField(
        primary_key=True, db_column="MissionQuestionId"
    )  # Identity field
    QuestionId = models.CharField(
        # max_length=10, editable=False, db_column="QuestionId", unique=True
     max_length=10, editable=False, db_column="QuestionId", unique=True
    )
    Direction = models.TextField(null=True, db_column="Direction")  # NVARCHAR(MAX)
    QuestionText = models.TextField(db_column="QuestionText")  # NVARCHAR(MAX) NOT NULL
    Options = models.TextField(null=True, db_column="Options")  # NVARCHAR(MAX)
    Matches = models.TextField(null=True, db_column="Matches")  # NVARCHAR(MAX)
    Answer = models.TextField(null=True, db_column="Answer")  # NVARCHAR(MAX)
    Explanation = models.TextField(null=True, db_column="Explanation")  # NVARCHAR(MAX)
    KeyWord = models.TextField(null=True, db_column="KeyWord")  # NVARCHAR(MAX)
    CorrectMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="CorrectMark"
    )  # DECIMAL(9,3)
    IncorrectMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="IncorrectMark"
    )  # DECIMAL(9,3)
    SkipMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="SkipMark"
    )  # DECIMAL(9,3)
    AllotedTime = models.CharField(
        max_length=50, null=True, db_column="AllotedTime"
    )  # VARCHAR(50)
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")  # DATETIME
    IsActive = models.BooleanField(db_column="IsActive")  # BIT NOT NULL
    IsDeleted = models.BooleanField(db_column="IsDeleted")  # BIT NOT NULL
    # ParagraphId = models.IntegerField(null=True, db_column="ParagraphId")  # INT
    ParagraphId = models.ForeignKey(
        "ParagraphMaster",
        to_field="ParagraphId",
        on_delete=models.CASCADE,
        db_column="ParagraphId",
        related_name="MissionQueston_ParagraphId",
    )
    # QuestionTypeId = models.IntegerField(db_column="QuestionTypeId")  # INT NOT NULL
    QuestionTypeId = models.ForeignKey(
        QuestionTypeMaster,
        to_field="QuestionTypeId",
        on_delete=models.CASCADE,
        db_column="QuestionTypeId",
        related_name="MissionQueston_QuestionTypeId",
    )
    ImportCode = models.CharField(
        max_length=50, null=True, db_column="ImportCode"
    )  # VARCHAR(50)
    InstitutionId = models.IntegerField(db_column="InstitutionId")  # INT NOT NULL
    QText = models.TextField(null=True, db_column="QText")  # NVARCHAR(MAX)
    QOptions = models.TextField(null=True, db_column="QOptions")  # NVARCHAR(MAX)
    QExplanation = models.TextField(
        null=True, db_column="QExplanation"
    )  # NVARCHAR(MAX)
    QMatches = models.TextField(null=True, db_column="QMatches")  # NVARCHAR(MAX)
    IsIntegerType = models.IntegerField(null=True, db_column="IsIntegerType")  # INT
    AdditionalAnswer = models.TextField(
        null=True, db_column="AdditionalAnswer"
    )  # NVARCHAR(MAX)
    OptionFormat = models.IntegerField(null=True, db_column="OptionFormat")  # INT
    CreatedBy = models.TextField(null=True, db_column="CreatedBy")  # NVARCHAR(MAX)
    CreatedOn = models.DateTimeField(null=True, db_column="CreatedOn")  # DATETIME
    Concept = models.TextField(null=True, db_column="Concept")  # NVARCHAR(MAX)
    IsRangeType = models.BooleanField(null=True, db_column="IsRangeType")  # BIT
    DOKLevel = models.IntegerField(null=True, db_column="DOKLevel")  # INT
    LearningOutcome = models.TextField(
        null=True, db_column="LearningOutcome"
    )  # NVARCHAR(MAX)
    MappedContent = models.TextField(
        null=True, db_column="MappedContent"
    )  # NVARCHAR(MAX)
    StatusTypeId = models.IntegerField(null=True, db_column="StatusTypeId")  # INT
    IsQuestionFlagged = models.BooleanField(
        null=True, db_column="IsQuestionFlagged"
    )  # BIT
    Source = models.TextField(null=True, db_column="Source")  # Added missing field
    PublishOn = models.DateTimeField(null=True, db_column="PublishOn")  # Added missing field
    PublishBy = models.CharField(max_length=450, null=True, db_column="PublishBy")  # Added missing field


    class Meta:
        db_table = "MissionQuestion"
        managed = False


class MissionQuestionMap(models.Model):
    MQMapID = models.BigAutoField(primary_key=True, db_column="MQMapID")
    MissionQuestionId = models.ForeignKey(
        MissionQuestion,
        on_delete=models.CASCADE,
        db_column="MissionQuestionId",
        related_name="MissionTestQuestionResult_MissionQuestioId",
    )
    QuestId = models.CharField(max_length=50, null=True, db_column="QuestId")
    MissionId = models.CharField(max_length=50, null=True, db_column="MissionId")
    OperationId = models.CharField(max_length=50, null=True, db_column="OperationId")
    TaskId = models.CharField(max_length=50, null=True, db_column="TaskId")
    SubTaskId = models.CharField(max_length=50, null=True, db_column="SubTaskId")
    DifficultyLevel = models.CharField(
        max_length=50, null=True, db_column="DifficultyLevel"
    )
    CorrectMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="CorrectMark"
    )
    IncorrectMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="IncorrectMark"
    )
    SkipMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="SkipMark"
    )
    AllotedTime = models.CharField(max_length=50, null=True, db_column="AllotedTime")
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")
    IsActive = models.BooleanField(db_column="IsActive")
    IsDeleted = models.BooleanField(db_column="IsDeleted")
    Concept = models.TextField(null=True, db_column="Concept")
    SourceTag = models.TextField(null=True, db_column="SourceTag")
    Tagging = models.CharField(max_length=500, null=True, db_column="Tagging")
    TypeOfQuestion = models.TextField(null=True, db_column="TypeOfQuestion")
    QuestionSubType = models.TextField(null=True, db_column="QuestionSubType")
    BloomId = models.IntegerField(null=True, db_column="BloomId")
    DOKLevel = models.IntegerField(null=True, db_column="DOKLevel")
    QID = models.ForeignKey(
        Quest,
        to_field="QId",
        on_delete=models.CASCADE,
        db_column="QID",
        related_name="MissionQuestionMap_QID",
    )
    MiId = models.ForeignKey(
        Mission,
        to_field="MiId",
        on_delete=models.CASCADE,
        db_column="MiId",
        related_name="MissionQuestionMap_MiId",
    )
    OId = models.ForeignKey(
        "common.Operation",
        to_field="OId",
        on_delete=models.CASCADE,
        db_column="OId",
        related_name="MissionQuestionMap_OId",
    )

    class Meta:
        db_table = "MissionQuestionMap"
        managed = False


class ParagraphTag(models.Model):
    # Fields matching the exact column names
    ParagraphTagID = models.BigAutoField(primary_key=True)

    # ForeignKey relation to ParagraphMaster with matching column name
    ParagraphID = models.ForeignKey(
        "ParagraphMaster", on_delete=models.CASCADE, db_column="ParagraphID"
    )

    CourseCode = models.CharField(max_length=50, null=True, blank=True)
    MissionId = models.CharField(max_length=50, null=True, blank=True)
    OperationId = models.CharField(max_length=50, null=True, blank=True)
    TaskId = models.CharField(max_length=50, null=True, blank=True)
    SubTaskId = models.CharField(max_length=50, null=True, blank=True)

    ModifiedOn = models.DateTimeField(default=timezone.now)

    IsActive = models.BooleanField(default=True)
    IsDeleted = models.BooleanField(default=False)

    # Meta options
    class Meta:
        db_table = "ParagraphTag"  # Explicitly specifying the table name
        ordering = ["ParagraphTagID"]

    # String representation for easier identification in queries/admin
    def __str__(self):
        return f"ParagraphTag {self.ParagraphTagID} for Paragraph {self.ParagraphID_id}"

