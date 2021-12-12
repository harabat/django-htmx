from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import Article


class Home(TemplateView):
    """all published articles"""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.order_by("-created_at")
        return context


class ArticleDetailView(DetailView):
    """detail view for individual articles"""

    model = Article
    template_name = "article_detail.html"


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
    # template_name = "editor_delete.html"
    template_name = "article_detail.html"
