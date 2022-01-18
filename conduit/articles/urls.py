from django.urls import path
from .views import (
    Home,
    EditorCreateView,
    EditorUpdateView,
    EditorDeleteView,
    ArticleCommentView,
    CommentDeleteView,
    ArticleFavoriteView,
    TagAddView,
    TagDeleteView,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("feed", Home.as_view(), name="home_feed"),
    path("article/<slug:slug>", ArticleCommentView.as_view(), name="article_detail"),
    path("editor", EditorCreateView.as_view(), name="editor_create"),
    path("editor/<slug:slug>", EditorUpdateView.as_view(), name="editor_update"),
    path("editor/<slug:slug>/delete", EditorDeleteView.as_view(), name="editor_delete"),
    path(
        "article/<slug:slug>/comment/<int:pk>/delete",
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
    path(
        "article/<slug:slug>/favorite",
        ArticleFavoriteView.as_view(),
        name="article_favorite",
    ),
    # path("article/<slug:article_slug>/tag", TagAddView.as_view(), name="article_tag"),
    # path(
    #     "article/<slug:article_slug>/tag/<slug:tag_slug>/delete",
    #     TagDeleteView.as_view(),
    #     name="tag_delete",
    # ),
]
