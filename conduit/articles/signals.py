from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Article
from .utils import slug_uuid_generator


@receiver(pre_save, sender=Article)
def generate_slug_uuid_before_article_save(sender, instance, *args, **kwargs):
    """Call slug_uuid_generator function when saving `Article` instance."""
    instance.slug_uuid = slug_uuid_generator(instance)
