from django.db import models
from apps.common.models.quest import Quest
from apps.common.models.institution import Institutions
from apps.common.models.location import Location
from apps.common.models.mission import Mission, MissionQuestion
from apps.common.models.operation import Operation

def get_UsersIdentity():
    from apps.accounts.models.user import UsersIdentity
    return UsersIdentity

def get_GroupMaster():
    from apps.accounts.models.user import GroupMaster
    return GroupMaster


# Create your models here.
class TestType(models.Model):
    test_type_id = models.AutoField(
        primary_key=True, db_column="TestTypeId"
    )  # IDENTITY (1, 1) translates to AutoField
    test_type_code = models.CharField(
        max_length=50, null=True, blank=True, db_column="TestTypeCode"
    )
    test_type_name = models.CharField(max_length=250, db_column="TestTypeName")
    is_active = models.BooleanField(db_column="IsActive")
    is_deleted = models.BooleanField(db_column="IsDeleted")

    class Meta:
        db_table = "TestType"
        managed = False

    def __str__(self):
        return self.test_type_name


class MissionTest(models.Model):
    MissionTestId = models.AutoField(
        primary_key=True, db_column="MissionTestId"
    )  # Identity field
    TestId = models.CharField(
        max_length=10, editable=False, unique=True, db_column="TestId"
    )
    TestName = models.CharField(
        max_length=250, null=True, db_column="TestName"
    )  # NVARCHAR(250)
    TestDescription = models.TextField(
        null=True, db_column="TestDescription"
    )  # NVARCHAR(MAX)
    TestDirections = models.TextField(
        null=True, db_column="TestDirections"
    )  # NVARCHAR(MAX)
    InstitutionId = models.IntegerField(db_column="InstitutionId")  # INT NOT NULL

    TestTypeId = models.ForeignKey(
        TestType,
        to_field="test_type_id",
        on_delete=models.DO_NOTHING,
        db_column="TestTypeId",
        related_name="MissionTest_TestTypeId",
    )

    Duration = models.CharField(
        max_length=50, null=True, db_column="Duration"
    )  # VARCHAR(50)
    TotalQuestion = models.IntegerField(null=True, db_column="TotalQuestion")  # INT
    TotalMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="TotalMark"
    )  # DECIMAL(9,3)
    PassMark = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, db_column="PassMark"
    )  # DECIMAL(9,3)
    IsActive = models.BooleanField(db_column="IsActive")  # BIT NOT NULL
    IsDeleted = models.BooleanField(db_column="IsDeleted")  # BIT NOT NULL
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")  # DATETIME
    TemplateId = models.IntegerField(null=True, db_column="TemplateID")  # INT
    IsDisplayMarksQues = models.BooleanField(
        null=True, db_column="IsDisplayMarksQues"
    )  # BIT
    ChapterCodes = models.TextField(
        null=True, db_column="ChapterCodes"
    )  # NVARCHAR(MAX)
    RulesJson = models.TextField(null=True, db_column="RulesJson")  # NVARCHAR(MAX)
    BoardCode = models.TextField(null=True, db_column="BoardCode")  # NVARCHAR(MAX)
    CourseCode = models.ForeignKey(
        Quest,
        to_field="QuestId",
        on_delete=models.DO_NOTHING,
        db_column="CourseCode",
        related_name="MissionTest_QuestId",
    )
    Level1Id = models.ForeignKey(
        Mission,
        to_field="MissionId",
        on_delete=models.DO_NOTHING,
        db_column="Level1Id",
        related_name="MissionTest_MissionId",
    )
    Level2Id = models.ForeignKey(
        Operation,
        to_field="OperationId",
        on_delete=models.DO_NOTHING,
        db_column="Level2Id",
        related_name="MissionTest_OperationId",
    )
    Level3Id = models.CharField(
        max_length=50, null=True, db_column="Level3Id"
    )  # VARCHAR(50)
    Level4Id = models.TextField(null=True, db_column="Level4Id")  # NVARCHAR(MAX)
    TestTime = models.IntegerField(null=True, db_column="TestTime")  # INT
    HasSection = models.BooleanField(null=True, db_column="HasSection")  # BIT
    TotalDuration = models.IntegerField(null=True, db_column="TotalDuration")  # INT
    CreatedOn = models.DateTimeField(null=True, db_column="CreatedOn")  # DATETIME
    PdfUrl = models.TextField(null=True, db_column="PDF_Url")  # NVARCHAR(MAX)
    PdfWithSolutionUrl = models.TextField(
        null=True, db_column="PDFWithSolution_Url"
    )  # NVARCHAR(MAX)
    IsPdfChanged = models.BooleanField(null=True, db_column="IsPdfChanged")  # BIT
    TestJsonUrl = models.TextField(null=True, db_column="TestJSON_URL")  # NVARCHAR(MAX)
    QrCode = models.CharField(
        max_length=50, null=True, db_column="QRCode"
    )  # VARCHAR(50)
    QrCodePath = models.TextField(null=True, db_column="QRCodePath")  # NVARCHAR(MAX)
    IsGroupTest = models.BooleanField(null=True, db_column="IsGroupTest")  # BIT
    TestGroupId = models.IntegerField(null=True, db_column="TestGroupId")  # INT
    TestJsonUrlBase64 = models.TextField(
        null=True, db_column="TestJSON_URL_base64"
    )  # NVARCHAR(MAX)
    TestHeaderText = models.TextField(
        null=True, db_column="TestHeaderText"
    )  # NVARCHAR(MAX)
    IsSubjective = models.BooleanField(null=True, db_column="IsSubjective")  # BIT
    SubjectIds = models.TextField(null=True, db_column="SubjectIds")  # NVARCHAR(MAX)
    ChapterIds = models.TextField(null=True, db_column="ChapterIds")  # NVARCHAR(MAX)
    IsContinuesSeq = models.BooleanField(null=True, db_column="IsContinuesSeq")  # BIT

    class Meta:
        db_table = "MissionTest"
        managed = False


class OnlineAssignTestDetail(models.Model):
    GroupMaster = get_GroupMaster()
    UsersIdentity = get_UsersIdentity()
    OnlineAssignTestId = models.AutoField(
        primary_key=True, db_column="OnlineAssignTestId"
    )
    TestId = models.ForeignKey(
        MissionTest,
        to_field="MissionTestId",
        on_delete=models.CASCADE,
        db_column="TestId",
    )
    CourseCode = models.ForeignKey(
        Quest, to_field="QuestId", on_delete=models.CASCADE, db_column="CourseCode"
    )
    TestAssignStartDate = models.DateTimeField(
        null=True, blank=True, db_column="TestAssignStartDate"
    )
    TestAssignEndDate = models.DateTimeField(
        null=True, blank=True, db_column="TestAssignEndDate"
    )
    NoOfAttempt = models.IntegerField(default=0, db_column="NoOfAttempt")
    TestTotalMarks = models.DecimalField(
        max_digits=9, decimal_places=3, default=0.0, db_column="TestTotalMarks"
    )
    TotalQuestion = models.IntegerField(default=0, db_column="TotalQuestion")
    IsDemo = models.BooleanField(default=False, null=True, db_column="IsDemo")
    TestDuration = models.IntegerField(null=True, blank=True, db_column="TestDuration")
    InstitutionId = models.ForeignKey(
        Institutions, on_delete=models.CASCADE, db_column="InstitutionId"
    )
    CenterId = models.ForeignKey(
        Location, to_field="LocationId", on_delete=models.CASCADE, db_column="CenterId"
    )
    BatchId = models.ForeignKey(
        GroupMaster, to_field="GroupId", on_delete=models.CASCADE, db_column="BatchId"
    )
    AssignTestDescription = models.CharField(
        max_length=1000, null=True, blank=True, db_column="AssignTestDescription"
    )
    AppliedTemplate = models.IntegerField(
        default=0, null=True, db_column="AppliedTemplate"
    )
    ReportTemplateId = models.IntegerField(
        null=True, blank=True, db_column="ReportTemplateId"
    )
    PropertJSON = models.TextField(null=True, blank=True, db_column="PropertJSON")
    CreatedOn = models.DateTimeField(
        default=models.functions.Now, db_column="CreatedOn"
    )
    CreatedBy = models.CharField(
        max_length=50, null=True, blank=True, db_column="CreatedBy"
    )
    IsDeleted = models.BooleanField(default=False, db_column="IsDeleted")
    TestTypeId = models.IntegerField(null=True, blank=True, db_column="TestTypeId")
    TestTagID = models.IntegerField(null=True, blank=True, db_column="TestTagID")
    IsTestResume = models.BooleanField(null=True, blank=True, db_column="IsTestResume")
    IsQuestionRandomization = models.BooleanField(
        null=True, blank=True, db_column="IsQuestionRandomization"
    )
    TestSeriesId = models.IntegerField(null=True, blank=True, db_column="TestSeriesId")
    ModifiedBy = models.CharField(
        max_length=50, null=True, blank=True, db_column="ModifiedBy"
    )
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    UserId = models.TextField(null=True, blank=True, db_column="UserId")
    # ReviewerId = models.CharField(
    #     max_length=50, null=True, blank=True, db_column="ReviewerId"
    # )

    ReviewerId = models.ForeignKey(
        UsersIdentity,
        to_field="UserId",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="ReviewerId",
    )
    IsAnswerUploadQuestionwise = models.BooleanField(
        null=True, blank=True, db_column="IsAnswerUploadQuestionwise"
    )
    TestGroupId = models.IntegerField(null=True, blank=True, db_column="TestGroupId")
    IsPracticeTest = models.BooleanField(
        null=True, blank=True, db_column="IsPracticeTest"
    )
    TestAlternateName = models.CharField(
        max_length=200, null=True, blank=True, db_column="TestAlternateName"
    )
    IsShowSolutionAfterTest = models.BooleanField(
        null=True, blank=True, db_column="IsShowSolutionAfterTest"
    )
    LID = models.ForeignKey(
        Location,
        to_field="LID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="LID",
        related_name="online_assign_test_detail_lid",
    )
    GID = models.ForeignKey(
        GroupMaster,
        to_field="GID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GID",
        related_name="online_assign_test_detail_gid",
    )
    QID = models.ForeignKey(
        Quest,
        to_field="QId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="QID",
        related_name="online_assign_test_detail_gid",
    )

    class Meta:
        db_table = "OnlineAssignTestDetail"
        managed = (
            False  # Set to False if you do not want Django to manage the table schema
        )


class MissionTestSummaryResult(models.Model):
    GroupMaster = get_GroupMaster()
    UsersIdentity = get_UsersIdentity()
    OnlineStudentAssignmentId = models.IntegerField(
        primary_key=True, db_column="OnlineStudentAssignmentId"
    )
    MissionTestSummaryResultId = models.CharField(
        max_length=100, null=True, db_column="MissionTestSummaryResultId"
    )

    UserId = models.ForeignKey(
        UsersIdentity,
        to_field="UserId",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="UserId",
        related_name="mission_test_results",  # Custom related name
    )
    LocationId = models.CharField(
        max_length=50, null=True, blank=True, db_column="LocationId"
    )
    GroupId = models.CharField(
        max_length=50, null=True, blank=True, db_column="GroupId"
    )
    QuestId = models.ForeignKey(
        Quest,
        to_field="QuestId",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="QuestId",
    )
    ContentId = models.CharField(
        max_length=50, null=True, blank=True, db_column="ContentId"
    )
    TestId = models.ForeignKey(
        MissionTest,
        to_field="TestId",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="TestId",
        related_name="MissionTestSummaryResult_testid",
    )
    ActualDuration = models.IntegerField(null=False, db_column="ActualDuration")
    AttemptedDuration = models.IntegerField(null=False, db_column="AttemptedDuration")
    TotalMarks = models.IntegerField(null=False, db_column="TotalMarks")
    MarksObtained = models.IntegerField(null=False, db_column="MarksObtained")
    AttemptedCount = models.IntegerField(null=False, db_column="AttemptedCount")
    TotalQuestion = models.IntegerField(null=False, db_column="TotalQuestion")
    FirstAttemptMark = models.IntegerField(null=False, db_column="FirstAttemptMark")
    Points = models.DecimalField(
        max_digits=18, decimal_places=0, null=True, blank=True, db_column="Points"
    )
    TestRankGroup = models.IntegerField(
        default=0, null=False, db_column="TestRankGroup"
    )
    TestRankLocation = models.IntegerField(
        default=0, null=False, db_column="TestRankLocation"
    )
    TestRankAllLocation = models.IntegerField(
        default=0, null=False, db_column="TestRankAllLocation"
    )
    IsDeleted = models.BooleanField(default=False, null=False, db_column="IsDeleted")
    CreatedOn = models.DateTimeField(null=True, blank=True, db_column="CreatedOn")
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column="ModifiedOn")
    LastAttemptMarks = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="LastAttemptMarks",
    )
    BestAttemptMarks = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="BestAttemptMarks",
    )
    BestAttemptNumber = models.IntegerField(
        null=True, blank=True, db_column="BestAttemptNumber"
    )
    CreatedBy = models.TextField(null=True, blank=True, db_column="CreatedBy")
    ModifiedBy = models.TextField(null=True, blank=True, db_column="ModifiedBy")
    AnswerSheetStatus = models.IntegerField(
        null=True, blank=True, db_column="AnswerSheetStatus"
    )
    DownloadLink = models.TextField(null=True, blank=True, db_column="DownloadLink")

    OnlineAssignTestId = models.ForeignKey(
        OnlineAssignTestDetail,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="OnlineAssignTestId",
        related_name="mission_test_results",  # Custom related name
    )
    TestTime = models.IntegerField(null=True, blank=True, db_column="TestTime")
    IsReportGenerated = models.BooleanField(
        null=True, blank=True, db_column="IsReportGenerated"
    )
    ReportPath = models.CharField(
        max_length=200, null=True, blank=True, db_column="ReportPath"
    )
    QRcode = models.CharField(max_length=50, null=True, blank=True, db_column="QRcode")
    IsOfflineDownload = models.BooleanField(
        null=True, blank=True, db_column="IsOfflineDownload"
    )

    LID = models.ForeignKey(
        Location,
        to_field="LID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="LID",
        related_name="mission_test_summary_result_lid",
    )
    GID = models.ForeignKey(
        GroupMaster,
        to_field="GID",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GID",
        related_name="mission_test_summary_result_gid",
    )
    QID = models.ForeignKey(
        Quest,
        to_field="QId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="QID",
        related_name="mission_test_summary_result_gid",
    )
    MissionTestId = models.ForeignKey(
        MissionTest,
        to_field="MissionTestId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="MissionTestId",
        related_name="mission_test_summary_result_missiontestId",
    )

    # MissionTestId
    class Meta:
        db_table = "MissionTestSummaryResult"
        managed = (
            False  # Set to False if you do not want Django to manage the table schema
        )
        # indexes = [
        #     models.Index(
        #         fields=["OnlineAssignTestId"], name="NCI_MissionTestSummaryResult_OATId"
        #     ),
        #     models.Index(
        #         fields=["QuestId"], name="NCI_MissionTestSummaryResult_QI_UCPM"
        #     ),
        #     models.Index(fields=["QuestId"], name="NCI_MTSR_UID_CID"),
        #     models.Index(
        #         fields=["OnlineStudentAssignmentId"],
        #         name="NCI_MissionTestSummaryResult_OSAI",
        #     ),
        # ]


class MissionTestQuestionResult(models.Model):
    UsersIdentity = get_UsersIdentity()
    MissionTestQuestionResultId = models.CharField(
        max_length=100,
        db_column="MissionTestQuestionResultId",
    )
    OnlineStudentAssignmentAttemptDetailsId = (
        models.AutoField(  # Primary keys cannot be null
            primary_key=True,
            db_column="OnlineStudentAssignmentAttemptDetailsId"
        )
    )
    OnlineStudentAssignmentAttemptId = models.IntegerField(
        db_column="OnlineStudentAssignmentAttemptId"
    )

    MissionTestIndividualResultId = models.CharField(
        max_length=100, db_column="MissionTestIndividualResultId"
    )
    UserId = models.ForeignKey(
        UsersIdentity,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        related_name="MissionTestQuestionResult_UserId",
    )
    TestId = models.ForeignKey(
        MissionTest,
        to_field="TestId",
        on_delete=models.DO_NOTHING,
        db_column="TestId",
        related_name="MissionTestQuestionResult_TestId",
    )
    QuestionId = models.ForeignKey(
        MissionQuestion,
        to_field="QuestionId",
        on_delete=models.CASCADE,
        db_column="QuestionId",
        related_name="MissionTestQuestionResult_QuestionId",
    )
    IsSkipped = models.BooleanField(null=True, db_column="IsSkipped")
    IsCorrect = models.BooleanField(null=True, db_column="IsCorrect")
    UserAnswer = models.TextField(null=True, db_column="UserAnswer")  # NVARCHAR(MAX)
    Marks = models.IntegerField(db_column="Marks")
    MarksObtained = models.IntegerField(db_column="MarksObtained")
    Duration = models.IntegerField(null=True, db_column="Duration")
    Comments = models.TextField(null=True, db_column="Comments")  # NVARCHAR(MAX)
    AnswerOrderSeq = models.CharField(
        max_length=50, null=True, db_column="AnswerOrderSeq"
    )
    CreatedOn = models.DateTimeField(null=True, db_column="CreatedOn")
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")
    TestQuestionId = models.IntegerField(null=True, db_column="TestQuestionId")
    TestSectionId = models.IntegerField(null=True, db_column="TestSectionId")
    AnswerSelected = models.TextField(
        null=True, db_column="AnswerSelected"
    )  # NVARCHAR(MAX)
    AttemptedAnswer = models.TextField(
        null=True, db_column="AttemptedAnswer"
    )  # NVARCHAR(MAX)
    IsQuestionSubmitted = models.BooleanField(null=True, db_column="IsQuestonSubmitted")
    MarkForReview = models.BooleanField(null=True, db_column="MarkforReview")
    AnsweredMarkedForReview = models.BooleanField(
        null=True, db_column="AnsweredMarkedforReview"
    )
    CreatedBy = models.TextField(null=True, db_column="CreatedBy")  # NVARCHAR(MAX)
    ModifiedBy = models.TextField(null=True, db_column="ModifiedBy")  # NVARCHAR(MAX)
    IsDeleted = models.BooleanField(null=True, db_column="IsDeleted")
    DeviceUniqueId = models.TextField(
        null=True, db_column="DeviceUniqueID"
    )  # NVARCHAR(MAX)
    QuestionTagId = models.IntegerField(null=True, db_column="QuestionTagId")
    StudentAttachments = models.TextField(
        null=True, db_column="StudentAttachments"
    )  # NVARCHAR(MAX)
    TeacherComments = models.TextField(
        null=True, db_column="TeacherComments"
    )  # NVARCHAR(MAX)
    TeacherAttachments = models.TextField(
        null=True, db_column="TeacherAttachments"
    )  # NVARCHAR(MAX)
    IsPartialCorrect = models.BooleanField(null=True, db_column="IsPartialCorrect")
    IsLastUsed = models.BooleanField(null=True, db_column="IsLastUsed")
    OfflineRefAttemptDetailsId = models.IntegerField(
        null=True, db_column="OfflineRefAttemptDetailsId"
    )

    class Meta:
        db_table = "MissionTestQuestionResult"
        managed = False


class MissionTestMap(models.Model):
    MissionTestMapID = models.AutoField(primary_key=True)
    MissionTestId = models.ForeignKey(
        MissionTest,
        to_field="MissionTestId",
        on_delete=models.DO_NOTHING,
        db_column="MissionTestId",
        related_name="MissionTestId_MissionTestMap",
    )
    QuestId = models.CharField(max_length=50, null=True, blank=True)
    MissionId = models.CharField(max_length=50, null=True, blank=True)
    OperationId = models.CharField(max_length=50, null=True, blank=True)
    TaskId = models.CharField(max_length=50, null=True, blank=True)
    SubTaskId = models.CharField(max_length=50, null=True, blank=True)
    DifficultyLevel = models.CharField(max_length=10, null=True, blank=True)
    ModifiedOn = models.DateTimeField(null=True, blank=True)
    IsActive = models.BooleanField()
    IsDeleted = models.BooleanField()
    IsMaster = models.BooleanField(null=True, blank=True)
    CreatedBy = models.TextField(null=True, blank=True)
    CreatedOn = models.DateTimeField(null=True, blank=True)
    ModifiedBy = models.TextField(null=True, blank=True)
    InstituteId = models.ForeignKey(
        Institutions,
        to_field="InstitutionId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="InstituteId",
        related_name="InstituteId_MissionTestMap",
    )

    class Meta:
        db_table = "MissionTestMap"

    def __str__(self):
        return f"MissionTestMap {self.mission_test_map_id}"


class PaperTemplateMaster(models.Model):
    TemplateId = models.AutoField(primary_key=True, db_column="TemplateId")
    HeaderHtml = models.TextField(null=True, db_column="HeaderHtml")
    HtmlDesign = models.TextField(null=True, db_column="HtmlDesign")
    QuestionDesign = models.TextField(null=True, db_column="QuestionDesign")
    TemplateName = models.CharField(max_length=150, null=True, db_column="TemplateName")
    TotalMarks = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, db_column="TotalMarks"
    )
    TestTime = models.CharField(max_length=100, null=True, db_column="TestTime")
    RulesJson = models.TextField(null=True, db_column="RulesJson")
    SubjectId = models.CharField(max_length=100, null=True, db_column="SubjectId")
    CourseId = models.ForeignKey(
        Quest,
        to_field="QuestId",
        on_delete=models.DO_NOTHING,
        db_column="CourseId",
        related_name="PaperTemplateMaster_QuestId",
    )
    # SubjectId = models.ForeignKey(
    #     Mission,
    #     to_field="MissionId",
    #     on_delete=models.DO_NOTHING,
    #     db_column="SubjectId",
    #     related_name="PaperTemplateMaster_MissionId",
    # )
    IsActive = models.BooleanField(db_column="IsActive")
    IsDeleted = models.BooleanField(db_column="IsDeleted")
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")
    HasSection = models.BooleanField(null=True, db_column="HasSection")
    SectionDesign = models.TextField(null=True, db_column="SectionDesign")
    TestType = models.ForeignKey(
        TestType,
        to_field="test_type_id",
        on_delete=models.DO_NOTHING,
        db_column="TestType",
        related_name="PaperTemplateMaster_TestTypeId",
    )
    InstitutionId = models.IntegerField(db_column="InstitutionId")
    IsSubjective = models.BooleanField(null=True, db_column="IsSubjective")
    InstructionSet1 = models.TextField(null=True, db_column="InstructionSet1")
    InstructionSet2 = models.TextField(null=True, db_column="InstructionSet2")
    P_BoardId = models.CharField(max_length=50, null=True, db_column="P_BoardId")
    P_GradeId = models.CharField(max_length=50, null=True, db_column="P_GradeId")
    P_SubjectId = models.IntegerField(null=True, db_column="P_SubjectId")
    SubjectIds = models.TextField(null=True, db_column="SubjectIds")
    HeaderTemplateId = models.IntegerField(null=True, db_column="HeaderTemplateId")
    RefrenceTemplateId = models.IntegerField(null=True, db_column="RefrenceTemplateId")
    ShowCombineChapter = models.IntegerField(null=True, db_column="ShowCombineChapter")

    class Meta:
        db_table = "PaperTemplateMaster"
        managed = (
            False  # If you want Django to use the existing table without creating it
        )


class TemplateTagMaster(models.Model):
    TemplateTagId = models.AutoField(primary_key=True, db_column="TemplateTagId")
    TemplateId = models.ForeignKey(
        PaperTemplateMaster,
        to_field="TemplateId",
        on_delete=models.DO_NOTHING,
        db_column="TemplateId",
        related_name="TemplateTagMaster_TemplateId",
    )

    CourseId = models.ForeignKey(
        Quest,
        to_field="QuestId",
        on_delete=models.DO_NOTHING,
        db_column="CourseId",
        related_name="TemplateTagMaster_QuestId",
    )
    Level1Id = models.ForeignKey(
        Mission,
        to_field="MissionId",
        on_delete=models.DO_NOTHING,
        db_column="Level1Id",
        related_name="TemplateTagMaster_MissionId",
    )
    IsActive = models.BooleanField(null=True, db_column="IsActive")
    IsDeleted = models.BooleanField(null=True, db_column="IsDeleted")
    CreatedBy = models.CharField(max_length=50, null=True, db_column="CreatedBy")
    CreatedOn = models.DateTimeField(null=True, db_column="CreatedOn")
    ModifiedBy = models.CharField(max_length=50, null=True, db_column="ModifiedBy")
    ModifiedOn = models.DateTimeField(null=True, db_column="ModifiedOn")
    InstituteId = models.IntegerField(null=True, db_column="InstituteId")
    InstituteId = models.ForeignKey(
        Institutions,
        to_field="InstitutionId",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="InstituteId",
        related_name="TemplateTagMaster_InstituteId",
    )

    class Meta:
        db_table = "TemplateTagMaster"
        managed = (
            False  # If you want Django to use the existing table without creating it
        )

    def __str__(self):
        return f"TemplateTag {self.template_tag_id}"


class MissionTestIndividualResult(models.Model):
    MissionTestIndividualResultId = models.CharField(max_length=100, null=False)
    OnlineStudentAssignmentAttemptId = models.AutoField(primary_key=True)
    MissionTestSummaryResultId = models.CharField(max_length=100)
    ActualDuration = models.IntegerField()
    AttemptedDuration = models.IntegerField()
    TotalMarks = models.IntegerField()
    MarksObtained = models.IntegerField()
    TotalQuestion = models.IntegerField()
    SkipCount = models.IntegerField(null=True)
    RightCount = models.IntegerField(null=True)
    WrongCount = models.IntegerField(null=True)
    Percentage = models.DecimalField(max_digits=5, decimal_places=2)
    AttemptedDate = models.DateTimeField()
    CreatedOn = models.DateTimeField()

    # OnlineStudentAssignmentId = models.IntegerField(null=True)
    OnlineStudentAssignmentId = models.ForeignKey(
        MissionTestSummaryResult,
        to_field="OnlineStudentAssignmentId",
        on_delete=models.DO_NOTHING,
        db_column="OnlineStudentAssignmentId",
        related_name="MissionTestIndividualResult_OnlineStudentAssignmentId",
    )
    AttemptNumber = models.IntegerField(null=True)
    CompletedDate = models.DateTimeField(null=True)
    IsTestSubmitted = models.BooleanField(null=True)
    CreatedBy = models.TextField(null=True)
    ModifiedOn = models.DateTimeField(null=True)
    ModifiedBy = models.TextField(null=True)
    IsDeleted = models.BooleanField(null=True)
    DeviceUniqueID = models.TextField(null=True)
    AutoSubmit = models.BooleanField(null=True)
    ForcefulSubmit = models.BooleanField(null=True)
    QuestionSequence = models.TextField(null=True)
    TestSectionJson = models.TextField(null=True)
    IsReviewComplete = models.BooleanField(null=True)
    ReviewOn = models.DateTimeField(null=True)
    AttemptAttachments = models.TextField(null=True)
    CorrectedAttachment = models.TextField(null=True)
    isObtainedMarkOverall = models.BooleanField(null=True)
    OverallTeacherComments = models.TextField(null=True)

    class Meta:
        db_table = "MissionTestIndividualResult"
