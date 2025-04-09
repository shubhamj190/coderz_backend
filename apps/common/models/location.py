from django.db import models
from apps.common.models.institution import Institutions
# Create your models here.

class Location(models.Model):
    LID = models.AutoField(primary_key=True, db_column='LID')
    LocationId = models.CharField(max_length=50,unique=True,null=True, blank=True, db_column='LocationId')
    LocationName = models.CharField(max_length=100, null=False, blank=False, db_column='LocationName')
    IsActive = models.BooleanField(null=False, blank=False, db_column='IsActive')
    IsDeleted = models.BooleanField(null=False, blank=False, db_column='IsDeleted')
    InstitutionId = models.ForeignKey(
        Institutions,
        on_delete=models.DO_NOTHING,
        db_column='InstitutionId',
        related_name='institution_locations'
    )
    DoNotTrack = models.BooleanField(null=True, blank=True, db_column='DoNotTrack')
    ModifiedOn = models.DateTimeField(null=True, blank=True, db_column='ModifiedOn')
    IsErpUsed = models.BooleanField(null=True, blank=True, db_column='IsErpUsed')
    ERP_API_Url = models.TextField(null=True, blank=True, db_column='ERP_API_Url')
    LogoPath = models.CharField(max_length=250, null=True, blank=True, db_column='LogoPath')

    class Meta:
        db_table = 'Location'
        constraints = [
            models.UniqueConstraint(fields=['LID'], name='PK_LocationMaster'),
            models.UniqueConstraint(fields=['LocationId'], name='UQ_Location_LocationId')
        ]
        managed=False


class LocationContentStatus(models.Model):
    Id=models.AutoField(primary_key=True,db_column='Id')
    LocationId=models.CharField(max_length=50,unique=True,null=False,db_column='LocationId')# add foregin key
    Watch=models.BooleanField(default=False,null=False,db_column='Watch')
    Think=models.BooleanField(default=False,null=False,db_column='Think')
    Solve=models.BooleanField(default=False,null=False,db_column='Solve')
    Play=models.BooleanField(default=False,null=False,db_column='Play')

    class Meta:
        db_table='LocationContentStatus'
        managed=False
