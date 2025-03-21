from django.db import models

class Board(models.Model):
    BId = models.AutoField(primary_key=True, db_column='BId')
    BoardId = models.CharField(max_length=50, blank=True, null=True, db_column='BoardId')
    BoardName = models.CharField(max_length=200, blank=True, null=True, db_column='BoardName')
    BoardDisplayName = models.CharField(max_length=200, blank=True, null=True, db_column='BoardDisplayName')
    SequenceNo = models.IntegerField(db_column='SequenceNo')
    IsActive = models.BooleanField(db_column='IsActive')
    IsDeleted = models.BooleanField(db_column='IsDeleted')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    ModifiedBy = models.CharField(max_length=50, blank=True, null=True, db_column='ModifiedBy')

    class Meta:
        db_table = 'Board'
        managed = False  # Set to False if this table already exists and should not be managed by Django
    
    def save(self, *args, **kwargs):
        self.BoardId = self.BId
        super().save(*args, **kwargs)

    def __str__(self):
        return self.BoardName or f"Board {self.BId}"

class Grade(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    BoardId = models.CharField(max_length=50, blank=True, null=True, db_column='BoardId')
    GradeId = models.CharField(max_length=50, blank=True, null=True, db_column='GradeId')
    GradeName = models.CharField(max_length=50, blank=True, null=True, db_column='GradeName')
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    
    class Meta:
        db_table = 'Grade'
        # managed = False  # Set to False if the table is managed externally

    def save(self, *args, **kwargs):
        self.GradeId = self.id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.GradeName or f"Grade {self.id}"

class Division(models.Model):
    DivisionId = models.AutoField(primary_key=True, db_column='DivisionId')
    DivisionName = models.CharField(max_length=50, blank=True, null=True, db_column='DivisionName')
    IsActive = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        db_table = 'Division'
        # managed = False
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

    def __str__(self):
        return f"{self.DivisionName}"
    
class GradeDivisionMapping(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE, db_column='GradeId', related_name='grade_division_mappings')
    Division = models.ForeignKey(Division, on_delete=models.CASCADE, db_column='DivisionId', related_name="division_grades_mappings")
    IsActive = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        db_table = 'GradeDivisionMapping'
        unique_together = ('Grade', 'Division')  # Ensures no duplicate mappings

    def __str__(self):
        return f"{self.Grade.GradeName} -> {self.Division.DivisionName}"