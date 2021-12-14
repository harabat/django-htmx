from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
)
from django.urls import reverse_lazy, reverse
from .models import Article, Comment
from django.shortcuts import get_object_or_404, resolve_url


class Home(TemplateView):
    """all published articles"""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.order_by("-created_at")
        return context


class ArticleListView(ListView):
    """list articles"""

    model = Article
    template_name = "home.html"

    def get_queryset(self):
        return super().get_queryset()


class ArticleDetailView(DetailView):
    """detail view for individual articles"""

    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.model.slug
        return context


class EditorCreateView(CreateView):
    """create article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class EditorUpdateView(UpdateView):
    """edit article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"


class EditorDeleteView(DeleteView):
    """delete article"""

    model = Article
    success_url = reverse_lazy("home")
    template_name = "article_detail.html"


class CommentCreateView(CreateView):
    """create comment"""

    model = Comment
    fields = ["body"]
    template_name = "comment_create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.article = Article.objects.filter(
            slug=self.kwargs.get("slug")
        ).first()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    # def get_success_url(self):
    #     return resolve_url("home")
    # success_url = reverse_lazy("article_detail", kw={"slug": })
