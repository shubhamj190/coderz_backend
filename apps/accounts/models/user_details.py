from django.db import models
from .user import User

class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='details')
    ContactNo = models.CharField(max_length=15)
    AdditionalContactNo = models.CharField(max_length=15, blank=True, null=True)
    Address = models.TextField()
    Location = models.CharField(max_length=255)
    Pincode = models.CharField(max_length=10)
    CityCode = models.CharField(max_length=10)
    StateCode = models.CharField(max_length=10)
    CountryCode = models.CharField(max_length=10)
    LastUsedDevice = models.CharField(max_length=255, blank=True, null=True)
    PromoCode = models.CharField(max_length=50, blank=True, null=True)
    PromoRefCode = models.CharField(max_length=50, blank=True, null=True)
    ModifiedOn = models.DateTimeField(auto_now=True)
    CustomerGST = models.CharField(max_length=15, blank=True, null=True)
    UserSource = models.CharField(max_length=100, blank=True, null=True)
    SchoolName = models.CharField(max_length=255, blank=True, null=True)
    BoardId = models.IntegerField(blank=True, null=True)
    GradeId = models.IntegerField(blank=True, null=True)
    QuestId = models.IntegerField(blank=True, null=True)
    LastQuestAccessed = models.DateTimeField(blank=True, null=True)
    IsDirectUser = models.BooleanField(default=False)
    UTMData = models.JSONField(blank=True, null=True)
    AdmissionNo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'userdetails'

    def __str__(self):
        return f"Details for {self.user.UserName}"