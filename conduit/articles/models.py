from django.db import models
from django.conf import settings
from django.urls import reverse


class Article(models.Model):
    # slug for the article, for urls
    # slug = models.SlugField(db_index=True, max_length=100, unique=True, editable=True)

    # the title of the article
    title = models.CharField(max_length=100)

    # a short description of the content
    description = models.TextField(max_length=300)

    # the text of the article
    body = models.TextField()

    # the author of the article
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # related_name="articles"
    )

    # a timestamp representing when this object was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # will be helpful in the admin app later on
    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})
        # return reverse("article_detail", kwargs={"slug": self.slug})
