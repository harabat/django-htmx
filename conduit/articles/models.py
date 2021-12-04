from django.db import models
from django.conf import settings

# Create your models here.
class Article(models.Model):
    # the title of the article
    title = models.CharField(db_index=True, max_length=100)

    # the text of the article
    body = models.TextField()

    # a short description of the content
    description = models.TextField(max_length=300)

    # the author of the article
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        # related_name="articles"
    )

    # A timestamp representing when this object was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
