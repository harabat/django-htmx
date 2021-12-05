from django.utils.text import slugify
import uuid


def unique_slug_generator(instance):
    """generate a unique slug for Articles from the title and a UUID"""

    ArticleClass = instance.__class__

    # get max length of =slug= as defined in the Article model
    max_length = ArticleClass._meta.get_field("slug").max_length

    # create slug_uuid by concatenating slugified title and UUID
    slug = "{slug_field}-{uuid_field}".format(
        slug_field=slugify(instance.title)[: max_length - 36 - 1],
        uuid_field=str(instance.uuid_field),
    )

    # if the slug exists, make another one
    if ArticleClass.objects.filter(slug=slug).exists():
        return unique_slug_generator(instance)

    return slug
