from django.contrib import admin
from .models import Article, Comment


class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ("slug_uuid", "uuid_field")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
