from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, *args, **kwargs):
    if created:
        instance.profile = Profile.objects.create(user=instance)
