from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .utils import slug_uuid_generator

import uuid


class Article(models.Model):
    slug_uuid = models.SlugField(max_length=255, editable=False, unique=True)
    uuid_field = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    body = models.TextField()
    author = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField("articles.Tag", related_name="articles", blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug_uuid = slug_uuid_generator(self)
        super().save(*args, **kwargs)

    def add_tag(self, tag):
        slug = slugify(tag)
        tag_object, created = Tag.objects.get_or_create(tag=tag, slug=slug)
        self.tags.add(tag_object)

    def remove_tag(self, tag):
        tag_object = Tag.objects.get(tag=tag)
        self.tags.remove(tag_object)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.slug_uuid})


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        to_field="slug_uuid",
    )
    body = models.TextField()
    author = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:60] + "..."

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.article.slug_uuid})


class Tag(models.Model):
    tag = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.tag
