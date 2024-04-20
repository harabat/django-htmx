from django.utils.text import slugify


def slug_uuid_generator(instance):
    """Generate a unique slug_uuid for Articles from the title and a UUID."""
    # if the instance already has a `slug_uuid`, don't change it
    # to avoid changing URLs
    if instance.slug_uuid:
        return instance.slug_uuid

    # get the instance's class (`Article`)
    ArticleClass = instance.__class__

    # get max length of `slug_uuid` as defined in the `Article` model
    max_length = ArticleClass._meta.get_field("slug_uuid").max_length

    uuid_field = str(instance.uuid_field)
    uuid_length = len(uuid_field)

    # slugify instance's title
    # trim slug to leave space for UUID
    slug_field = slugify(instance.title)[: max_length - uuid_length - 1]

    # create `slug_uuid` by concatenating slugified title and UUID
    slug_uuid = "{slug_field}-{uuid_field}".format(
        slug_field=slug_field,
        uuid_field=uuid_field,
    )

    return slug_uuid
