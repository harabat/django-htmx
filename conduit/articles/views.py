from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
    RedirectView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from .models import Article, Comment, Tag
from .forms import ArticleForm


class Home(TemplateView):
    """all published articles"""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["global_feed"] = Article.objects.order_by("-created_at")
        if self.request.user.is_authenticated:
            context["your_articles"] = Article.objects.filter(
                author__in=self.request.user.profile.follows.all()
            ).order_by("-created_at")
        else:
            context["your_articles"] = None
        return context


class ArticleDetailView(DetailView):
    """detail view for individual articles"""

    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentCreateView().get_form_class()
        if self.request.user.is_authenticated:
            context["is_following"] = self.request.user.profile.is_following(
                self.object.author
            )
        return context


class EditorCreateView(LoginRequiredMixin, CreateView):
    """create article"""

    model = Article
    form_class = ArticleForm
    # fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user.profile
        self.object.save()
        return super().form_valid(form)

    # def post(self, request, *args, **kwargs):
    #     if "add_new_tag" in request.POST:
    #         new_tag = self.request.POST.get("new_tag")
    #         if new_tag:
    #             article = self.get_object()
    #             article.add_tag(new_tag)
    #             # return redirect(
    #             #     reverse_lazy(
    #             #         "editor_create", kwargs={"slug": self.kwargs.get("slug")}
    #             #     )
    #             # )
    #             return super().post(request, *args, **kwargs)
    #         else:
    #             return super().post(request, *args, **kwargs)


class EditorUpdateView(LoginRequiredMixin, UpdateView):
    """edit article"""

    model = Article
    form_class = ArticleForm
    # fields = ["title", "description", "body"]
    template_name = "editor.html"

    def post(self, request, *args, **kwargs):
        if request.user == self.get_object().author.user:
            if "add_new_tag" in request.POST:
                new_tag = self.request.POST.get("new_tag")
                if new_tag:
                    article = self.get_object()
                    article.add_tag(new_tag)
                return redirect(
                    reverse_lazy(
                        "editor_update", kwargs={"slug": self.kwargs.get("slug")}
                    )
                )
            elif "remove_tag" in request.POST:
                tag = request.POST.get("remove_tag")
                article = self.get_object()
                article.remove_tag(tag)
                return redirect(
                    reverse_lazy(
                        "editor_update", kwargs={"slug": self.kwargs.get("slug")}
                    )
                )
            else:
                return super().post(request, *args, **kwargs)
        return redirect(self.get_object().get_absolute_url())


class EditorDeleteView(LoginRequiredMixin, DeleteView):
    """delete article"""

    model = Article
    success_url = reverse_lazy("home")
    template_name = "article_detail.html"

    def get_object(self):
        slug_uuid = self.kwargs.get("slug_uuid")
        return get_object_or_404(Article, slug_uuid=slug_uuid)

    def post(self, request, *args, **kwargs):
        if request.user == self.get_object().author.user:
            return super().post(request, *args, **kwargs)
        return redirect(self.get_object().get_absolute_url())


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

    def post(self, request, *args, **kwargs):
        if request.user == self.get_object().author.user:
            return super().post(request, *args, **kwargs)
        return redirect(self.get_object().get_absolute_url())

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug": self.kwargs.get("slug")})


class ArticleFavoriteView(RedirectView):
    pattern_name = "article_detail"

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get("next", None)
        if url:
            return url
        else:
            return super().get_redirect_url(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug", None)
        article = get_object_or_404(Article, slug=slug)
        if request.user.profile.has_favorited(article):
            request.user.profile.unfavorite(article)
        else:
            request.user.profile.favorite(article)
        return super().post(request, *args, **kwargs)


class TagAddView(UpdateView):
    """Add a tag to an Article object"""

    model = Article
    form_class = ArticleForm
    template_name = "editor.html"
    # success_url = reverse_lazy(
    #     "editor_update", kwargs={"slug": self.kwargs.get("article_slug")}
    # )

    def get(self, request, *args, **kwargs):
        import pudb

        pu.db
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        tag = self.request.form.tag
        import pudb

        pu.db
        return super().post(request, *args, **kwargs)


class TagDeleteView(DeleteView):
    model = Tag
    template_name = "article_tag.html"

    def get_success_url(self):
        return reverse(
            "article_detail", kwargs={"slug": self.kwargs.get("article_slug")}
        )
        return super().get_success_url()
