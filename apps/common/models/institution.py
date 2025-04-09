from django.db import models

# Create your models here.
class Institutions(models.Model):
    InstitutionId = models.AutoField(primary_key=True, db_column='InstitutionId')
    InstitutionName = models.CharField(max_length=100, null=False, blank=False, db_column='InstitutionName')
    EmailId = models.EmailField(max_length=200, db_column='EmailId')
    PhoneNo = models.CharField(max_length=50, null=True, blank=True, db_column='PhoneNo')
    Address = models.CharField(max_length=200, null=True, blank=True, db_column='Address')
    City = models.CharField(max_length=50, null=True, blank=True, db_column='City')
    State = models.CharField(max_length=50, null=True, blank=True, db_column='State')
    Country = models.CharField(max_length=100, null=True, blank=True, db_column='Country')
    Pin = models.CharField(max_length=15, null=True, blank=True, db_column='Pin')
    Logopath = models.CharField(max_length=150, null=False, blank=False, db_column='Logopath')
    ConfigJson = models.JSONField(null=True, blank=True, db_column='ConfigJson')
    ValidityEndDate = models.DateTimeField(null=True, blank=True, db_column='ValidityEndDate')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsActive = models.BooleanField(null=False, blank=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, blank=False, db_column='IsDeleted')

    class Meta:
        db_table = 'Institutions'
        constraints = [
            models.UniqueConstraint(fields=['InstitutionId'], name='PK_Institutions')
        ]
        managed=False

class ClassMaster(models.Model):
    ClassId = models.AutoField(primary_key=True, db_column='ClassId')
    ClassName = models.CharField(max_length=50, null=True, blank=True, db_column='ClassName')

    class Meta:
        db_table = 'ClassMaster'
        managed = False  # Set to False if you do not want Django to manage the table schema
        constraints = [
            models.UniqueConstraint(fields=['ClassId'], name='PK_ClassMaster')  # Ensure ClassId is unique
        ]

class SubClassMaster(models.Model):
    SubClassId = models.AutoField(primary_key=True, db_column='SubClassId')
    SubClassName = models.CharField(max_length=50, null=False, blank=False, db_column='SubClassName')
    ClassId = models.ForeignKey(
        ClassMaster, 
        on_delete=models.CASCADE, 
        db_column='ClassId', 
        related_name='subclasses'
    )

    class Meta:
        db_table = 'SubClassMaster'
        managed = False

class Board(models.Model):
    BId = models.AutoField(primary_key=True, db_column='BId')
    BoardId = models.CharField(max_length=50, null=True,unique=True, blank=True, db_column='BoardId')
    BoardName = models.CharField(max_length=200, null=True, blank=True, db_column='BoardName')
    BoardDisplayName = models.CharField(max_length=200, null=True, blank=True, db_column='BoardDisplayName')
    SequenceNo = models.IntegerField(null=False, db_column='SequenceNo')
    IsActive = models.BooleanField(null=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, db_column='IsDeleted')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    ModifiedBy = models.CharField(max_length=50, null=True, blank=True, db_column='ModifiedBy')

    class Meta:
        db_table = 'Board'
        managed = False 
