from django.db import models

from apps.common.models.mission import Mission

# Create your models here.

class Operation(models.Model):
    OId = models.AutoField(primary_key=True, db_column='OId')
    OperationId = models.CharField(max_length=50, null=True, blank=True, unique=True, db_column='OperationId')
    OperationName = models.CharField(max_length=200, null=False, blank=False, db_column='OperationName')
    OperationDisplayName = models.CharField(max_length=200, null=True, blank=True, db_column='OperationDisplayName')
    OperationDescription = models.CharField(max_length=250, null=True, blank=True, db_column='OperationDescription')
    SequenceNo = models.IntegerField(null=False, db_column='SequenceNo')
    MissionId = models.ForeignKey(
        Mission,
        to_field='MissionId',
        on_delete=models.CASCADE,
        db_column='MissionId',
        related_name='operations'
    )
    IsActive = models.BooleanField(null=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, db_column='IsDeleted')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    Operationicon = models.CharField(max_length=450, null=True, blank=True, db_column='Operationicon')
    Operationiconcolour = models.CharField(max_length=50, null=True, blank=True, db_column='Operationiconcolour')
    OperationB64 = models.TextField(null=True, blank=True, db_column='OperationB64')
    OperationIconName = models.CharField(max_length=500, null=True, blank=True, db_column='OperationIconName')
    VideoCount = models.IntegerField(null=True, blank=True, db_column='VideoCount')
    TestCount = models.IntegerField(null=True, blank=True, db_column='TestCount')
    ActivityCount = models.IntegerField(null=True, blank=True, db_column='ActivityCount')
    WebContentCount = models.IntegerField(null=True, blank=True, db_column='WebContentCount')
    RefOperationId = models.CharField(max_length=50, null=True, blank=True, db_column='RefOperationId')
    OPerationIconUrl = models.TextField(null=True, blank=True, db_column='OPerationIconUrl')

    class Meta:
        db_table = 'Operation'
        managed = False  # Set to False if you do not want Django to manage the table schema
        indexes = [
            models.Index(fields=['IsActive', 'IsDeleted'], name='NCI_Operation_OID'),
        ]


class Task(models.Model):
    TId = models.AutoField(primary_key=True, db_column='TId')
    TaskId = models.CharField(max_length=50, unique=True, null=True, blank=True, db_column='TaskId')
    TaskName = models.CharField(max_length=200, null=False, blank=False, db_column='TaskName')
    TaskDisplayName = models.CharField(max_length=200, null=True, blank=True, db_column='TaskDisplayName')
    TaskDescription = models.CharField(max_length=250, null=True, blank=True, db_column='TaskDescription')
    SequenceNo = models.IntegerField(null=False, db_column='SequenceNo')
    OperationId = models.ForeignKey(
        Operation,
        to_field='OperationId',
        on_delete=models.CASCADE,
        db_column='OperationId',
        related_name='task_operation'
    )
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsActive = models.BooleanField(null=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, db_column='IsDeleted')
    Taskicon = models.CharField(max_length=50, null=True, blank=True, db_column='Taskicon')
    Taskiconcolour = models.CharField(max_length=50, null=True, blank=True, db_column='Taskiconcolour')
    TaskB64 = models.TextField(null=True, blank=True, db_column='TaskB64')
    TaskIconName = models.CharField(max_length=500, null=True, blank=True, db_column='TaskIconName')
    VideoCount = models.IntegerField(null=True, blank=True, db_column='VideoCount')
    TestCount = models.IntegerField(null=True, blank=True, db_column='TestCount')
    ActivityCount = models.IntegerField(null=True, blank=True, db_column='ActivityCount')
    WebContentCount = models.IntegerField(null=True, blank=True, db_column='WebContentCount')
    RefTaskId = models.CharField(max_length=50, null=True, blank=True, db_column='RefTaskId')
    TaskIconUrl = models.TextField(null=True, blank=True, db_column='TaskIconUrl')

    class Meta:
        db_table = 'Task'
        managed = False  # Set to False if you do not want Django to manage the table schema
        constraints = [
            models.UniqueConstraint(fields=['TaskId'], name='UQ_Task_TaskId')  # Ensure TaskId is unique
        ]


class SubTask(models.Model):
    STId = models.AutoField(primary_key=True, db_column='STId')
    SubTaskId = models.CharField(max_length=50, unique=True, null=True, blank=True, db_column='SubTaskId')
    SubTaskName = models.CharField(max_length=200, null=False, blank=False, db_column='SubTaskName')
    SubTaskDisplayName = models.CharField(max_length=250, null=True, blank=True, db_column='SubTaskDisplayName')
    SubTaskDescription = models.CharField(max_length=500, null=True, blank=True, db_column='SubTaskDescription')
    SequenceNo = models.IntegerField(null=False, db_column='SequenceNo')
    TaskId = models.ForeignKey(
        Task,
        to_field='TaskId',
        on_delete=models.CASCADE,
        db_column='TaskId',
        related_name='subtask_task'
    )
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsActive = models.BooleanField(null=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, db_column='IsDeleted')
    SubTaskicon = models.CharField(max_length=50, null=True, blank=True, db_column='SubTaskicon')
    SubTaskiconcolour = models.CharField(max_length=50, null=True, blank=True, db_column='SubTaskiconcolour')
    SubTaskB64 = models.TextField(null=True, blank=True, db_column='SubTaskB64')
    SubTaskIconName = models.CharField(max_length=500, null=True, blank=True, db_column='SubTaskIconName')
    VideoCount = models.IntegerField(null=True, blank=True, db_column='VideoCount')
    TestCount = models.IntegerField(null=True, blank=True, db_column='TestCount')
    ActivityCount = models.IntegerField(null=True, blank=True, db_column='ActivityCount')
    WebContentCount = models.IntegerField(null=True, blank=True, db_column='WebContentCount')
    RefSubTaskId = models.CharField(max_length=50, null=True, blank=True, db_column='RefSubTaskId')
    SubTaskIconUrl = models.TextField(null=True, blank=True, db_column='SubTaskIconUrl')

    class Meta:
        db_table = 'SubTask'
        managed = False  # Set to False if you do not want Django to manage the table schema
        constraints = [
            models.UniqueConstraint(fields=['SubTaskId'], name='UQ_SubTask_SubTaskId')  # Ensure SubTaskId is unique
        ]


class QuestContent(models.Model):
    QCId = models.AutoField(primary_key=True)
    ContentId = models.CharField(max_length=9, editable=False)  # Computed field, requires manual handling or database constraint
    ContentName = models.CharField(max_length=100, null=True, blank=True)
    ContentDisplayName = models.CharField(max_length=200, null=True, blank=True)
    ContentDescription = models.TextField(null=True, blank=True)
    SequenceNo = models.IntegerField()
    FileUrl = models.TextField(null=True, blank=True)
    ImageUrl = models.CharField(max_length=200, null=True, blank=True)
    QuestId = models.CharField(max_length=50, null=True, blank=True)
    MissionId = models.ForeignKey(
        Mission,
        to_field='MissionId',
        on_delete=models.CASCADE,
        db_column='MissionId',
        related_name='QuestContent_MissionId'
    )
    # OperationId = models.CharField(max_length=50, null=True, blank=True)
    OperationId = models.ForeignKey(
        Operation,
        to_field='OperationId',
        on_delete=models.CASCADE,
        db_column='OperationId',
        related_name='QuestContent_OperationId'
    )
    TaskId = models.ForeignKey(
        Task,
        to_field='TaskId',
        on_delete=models.CASCADE,
        db_column='TaskId',
        related_name='QuestContent_TaskId'
    )
    SubTaskId = models.CharField(max_length=50, null=True, blank=True)
    ContentTypeCode = models.CharField(max_length=50, null=True, blank=True)
    TestId = models.ForeignKey(
        'Assesment.MissionTest',
        to_field='TestId',
        on_delete=models.CASCADE,
        db_column='TestId',
        related_name='QuestContent_TestId'
    )
    HTMLContent = models.TextField(null=True, blank=True)
    ContentProperty = models.TextField(null=True, blank=True)
    TotalContentRating = models.DecimalField(max_digits=18, decimal_places=1)
    TotalUserRatedContent = models.BigIntegerField()
    RatingModifiedOn = models.DateTimeField(null=True, blank=True)
    ModifiedOn = models.DateTimeField(null=True, blank=True)
    IsActive = models.BooleanField()
    IsDeleted = models.BooleanField()
    Points = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    ContentTime = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    FileName = models.TextField(null=True, blank=True)
    QRCode = models.TextField(null=True, blank=True)
    IsDynamicAssessment = models.BooleanField(null=True, blank=True)
    RefContentId = models.CharField(max_length=50, null=True, blank=True)
    RefQCId = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'QuestContent'
        managed = False
        indexes = [
            models.Index(fields=['IsActive', 'IsDeleted', 'QuestId'], name='nci_wi_QuestContent', include=['ContentTypeCode', 'MissionId', 'OperationId', 'Points', 'SubTaskId', 'TaskId']),
            models.Index(fields=['TestId', 'IsActive'], name='NCI_QuestContent_TId_A')
        ]