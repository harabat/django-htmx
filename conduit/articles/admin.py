from django.contrib import admin
from .models import Article

# only works in Django admin app
# class ArticleAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("title",)}

admin.site.register(Article)
