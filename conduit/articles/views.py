from django.shortcuts import render
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    View,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Article, Comment
import pudb


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


class ArticleDetailView(DetailView):
    """detail view for individual articles"""

    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentCreateView().get_form_class()
        return context


class EditorCreateView(LoginRequiredMixin, CreateView):
    """create article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user.profile
        self.object.save()
        return super().form_valid(form)

    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)


class EditorUpdateView(LoginRequiredMixin, UpdateView):
    """edit article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"


class EditorDeleteView(LoginRequiredMixin, DeleteView):
    """delete article"""

    model = Article
    success_url = reverse_lazy("home")
    template_name = "article_detail.html"


class CommentCreateView(LoginRequiredMixin, CreateView):
    """create comment"""

    model = Comment
    fields = ["body"]
    template_name = "article_detail.html"

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        form.instance.article = Article.objects.filter(
            slug=self.kwargs.get("slug")
        ).first()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug": self.object.article.slug})


class ArticleCommentView(View):
    """view article and post comments"""

    def get(self, request, *args, **kwargs):
        view = ArticleDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """delete comment"""

    model = Comment
    template_name = "article_detail.html"

    def get_success_url(self):
        # self.kwargs.get("slug") == self.object.article.slug
        return reverse("article_detail", kwargs={"slug": self.kwargs.get("slug")})
