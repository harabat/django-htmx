from django.urls import path
from .views import Home, ArticleDetailView

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("article/<int:pk>", ArticleDetailView.as_view(), name="article_detail"),
]
