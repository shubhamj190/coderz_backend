from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.accounts.models.user import GroupMaster
from .models import User, UserDetails

@receiver(post_save, sender=User)
def create_user_details(sender, instance, created, **kwargs):
    if created:
        UserDetails.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_details(sender, instance, **kwargs):
    instance.details.save()

@receiver(pre_save, sender=GroupMaster)
def set_group_id(sender, instance, **kwargs):
    """Automatically set GroupId before saving the model."""
    if not instance.GroupId:  # Ensure it only sets if not already assigned
        instance.GroupId = f"G{instance.GID}"