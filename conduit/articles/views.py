from django.shortcuts import render
from .models import Article


def home(request):
    """all published articles"""
    articles = Article.objects.order_by("-created_at")
    return render(request, "home.html", {"articles": articles})
