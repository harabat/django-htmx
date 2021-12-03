from django.shortcuts import render
from .models import Article


# def global_feed(request):
#     """all published articles"""
#     articles = Article.objects.order_by("-created_at")
#     # return render(request, "articles/global_feed.html", {"articles": articles})
#     return render(request, "base.html")
