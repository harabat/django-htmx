from django.urls import path
from .views import (
    Home,
    ArticleDetailView,
    EditorCreateView,
    EditorUpdateView,
    EditorDeleteView,
    CommentCreateView,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("article/<slug:slug>", ArticleDetailView.as_view(), name="article_detail"),
    path("editor", EditorCreateView.as_view(), name="editor_create"),
    path("editor/<slug:slug>", EditorUpdateView.as_view(), name="editor_update"),
    path("editor/<slug:slug>/delete", EditorDeleteView.as_view(), name="editor_delete"),
    path(
        "article/<slug:slug>/comment/",
        CommentCreateView.as_view(),
        name="comment_create",
    ),
]
