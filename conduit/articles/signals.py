from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Article
from conduit.utils import unique_slug_generator


@receiver(pre_save, sender=Article)
def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
