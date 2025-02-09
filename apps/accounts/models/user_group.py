from django.db import models
from django.contrib.auth.models import Group
from .user import User

class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    LocationId = models.IntegerField()
    ModifiedOn = models.DateTimeField(auto_now=True)
    IsDeleted = models.BooleanField(default=False)
    ImportCode = models.CharField(max_length=50, blank=True, null=True)
    Lid = models.IntegerField(blank=True, null=True)
    Gid = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'usergroup'
        unique_together = ('user', 'group', 'LocationId')

    def __str__(self):
        return f"{self.user} in {self.group} at {self.LocationId}"