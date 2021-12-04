from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("article/<str:slug>", views.article_view, name="article_view"),
]
