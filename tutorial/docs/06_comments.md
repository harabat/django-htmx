# Comments

## Introduction

Now that we have articles, we need comments. Gotta give our users a
voice, right?

## Model

A comment needs a related article, an author, a body, and a date. Let's
create a `Comment` model in `models.py`:

``` { .python }
# ...

class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        to_field="slug_uuid",
    )
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:60] + "..."

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.article.slug_uuid})
```

Let's `makemigrations` and `migrate`. You should get the following
error:

```
SystemCheckError: System check identified some issues:

ERRORS:
articles.Comment.article: (fields.E311) 'Article.slug_uuid' must be unique because it is referenced by a foreign key.
        HINT: Add unique=True to this field or add a UniqueConstraint (without condition) in the model Meta.constraints.
```

That's because we're using articles' `slug_uuid` fields as ForeignKeys
for the comments (so that we can filter our comments by the attached
articles' `slug_uuid` fields instead of their UUIDs). This error is
easily corrected by adding `unique=True` as an argument to the
`slug_uuid` field in the `Article` model in `models.py`. You should be
able to `makemigrations` and `migrate` after that.

Now, we need to register our model in `admin.py`:

``` { .python hl_lines="2 5" }
from django.contrib import admin
from .models import Article, Comment        # new

admin.site.register(Article)
admin.site.register(Comment)                # new
```

When this is done, go to your admin app and create a few comments for a
couple articles.

## Viewing comments

We want to be able to view the comments in our `article_detail.html`
template.

In `article_detail.html`:

``` { .html hl_lines="9-12" }
<div class="container page">
    <div class="row article-content">
        <div class="col-xs-12">
            <div>
                {{ article.body|linebreaks }}
            </div>
        </div>
    </div>
    <hr />                                  <!-- new -->
    <div class="row">                       <!-- new -->
        {% include 'comments.html' %}       <!-- new -->
    </div>                                  <!-- new -->
</div>
```

Now create `comments.html` in the `templates` folder and add the
following:

``` { .html }
<div class="col-xs-12 col-md-8 offset-md-2">
    {% for comment in article.comments.all|dictsortreversed:'created_at' %}
        <div class="card">
            <div class="card-block">
                <p class="card-text">
                    {{ comment.body }}
                </p>
            </div>
            <div class="card-footer">
                <span class="comment-author">
                    {{ comment.author.user.username }}
                </span>
                <span class="date-posted">
                    {{ comment.created_at|date:"D M d Y" }}
                </span>
            </div>
        </div>
    {% endfor %}
</div>
```

## Creating comments

We will now start allowing our users to leave comments on the website.
We could do this like in the Django Girls tutorial: the
`ArticleDetailView` would include a button that would direct to
`CommentCreateView` on a separate page, and saving the comment would
bring the user back to the `ArticleDetailView`. However, the
`RealWorldApp` allows users to create and save their comments directly
below the article, on the same page, so that's what we're going to try.

Surprisingly, this is not straightforward to implement in Django,
because it implies mixing `DetailView` and `CreateView` functionalities
in a single page, which is made difficult by the fact that the
`DetailView` doesn't have a POST method, while the `CreateView` requires
it. Fortunately, our use case is covered in the Django documentation:
<https://docs.djangoproject.com/en/4.0/topics/class-based-views/mixins/#an-alternative-better-solution>.

First, we'll create a `CommentCreateView` in `users/views.py`. We
override the `form_valid` method because we need to specify the `author`
and `article` fields required by the `Comment` model. We also override
the `get_success_url` because we want the user to be redirected to the
`ArticleDetailView` upon saving the comment.

``` { .python }
# ...
from .models import Article, Comment

# ...
class CommentCreateView(CreateView):
    """create comment"""

    model = Comment
    fields = ["body"]
    template_name = "article_detail.html"

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        form.instance.article = Article.objects.filter(
            slug_uuid=self.kwargs.get("slug_uuid")
        ).first()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.object.article.slug_uuid})
```

Now, we need to modify the `ArticleDetailView` to make the
`CommentCreateView`'s form available to `templates/article_detail.html`
through the `get_context_data` method:

``` { .python hl_lines="7-10" }
class ArticleDetailView(DetailView):
    """detail view for individual articles"""

    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):                   # new
        context = super().get_context_data(**kwargs)        # new
        context["form"] = CommentCreateView().get_form()    # new
        return context                                      # new
```

Finally, we create a view that combines `ArticleDetailView` and
`CommentCreateView`:

``` { .python }
# ...
from django.views.generic import (
    # ...
    View,
)


# ...
class ArticleCommentView(View):
    """view article and post comments"""

    def get(self, request, *args, **kwargs):
        view = ArticleDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)
```

We want this new hybrid view to be the one returned by the
`article/<slug:slug_uuid>` path: depending on whether the method is
`GET` or `POST`, the new view will either return the
`ArticleDetailView`, or the `CommentCreateView`.

In `urls.py`, we replace the `article_detail` path by the following:

``` { .python }
# ...
from .views import (
    # ...
    ArticleCommentView,
)

urlpatterns = [
    # ...
    path(
        "article/<slug:slug_uuid>",
        ArticleCommentView.as_view(),
        name="article_detail",
    ),
    # instead of =path("article/<slug:slug_uuid>", ArticleCommentView.as_view(), name="article_detail")=
]
```

Now that our views.py and urls.py are ready, we need to create the
templates.

Create `comment_create.html`, which corresponds to the
`CommentCreateView`'s form:

``` { .html }
{% block content %}
    <form
        class="card comment-form"
        method="post"
        action="{% url 'article_detail' slug_uuid=object.slug_uuid %}"
    >
        {% csrf_token %}
        <div class="card-block">
            <textarea
                class="form-control"
                rows="3"
                placeholder="Write a comment..."
                name="{{ form.body.name }}"
            >{{ form.body.value|default_if_none:'' }}</textarea>
        </div>
        <div class="card-footer">
            <button class="btn btn-sm btn-primary" type="submit">
                Post Comment
            </button>
        </div>
    </form>
{% endblock %}
```

In `comments.html`, we include the `comment_create.html` template:

``` { .html hl_lines="2-4" }
<div class="col-xs-12 col-md-8 offset-md-2">
    <div>                                           <!-- new -->
        {% include 'comment_create.html' %}         <!-- new -->
    </div>                                          <!-- new -->
    {% for comment in article.comments.all|dictsortreversed:'created_at' %}
    <!-- ... -->
```

Everything should be working now. Try to create some comments on an
article.

## Deleting comments

We now want to be able to delete comments.

In `articles/views.py`, add the `CommentDeleteView`:

``` { .python }
class CommentDeleteView(DeleteView):
    """delete comment"""

    model = Comment
    template_name = "article_detail.html"

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.object.article.slug_uuid})
```

In `urls.py`:

``` { .python }
urlpatterns = [
    # ...
    path(
        "article/<slug:slug_uuid>/comment/<int:pk>/delete",
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
```

We require `pk` as an argument because that's what the
`CommentDeleteView` needs to know which comment to delete. The
`<slug:slug_uuid>` part is unnecessary, but it makes the path more
logical, I find.

In `comments.html`:

``` { .html hl_lines="8" }
<div class="card-footer">
    <span class="comment-author">
        {{ comment.author }}
    </span>
    <span class="date-posted">
        {{ comment.created_at|date:"D M d Y" }}
    </span>
    {% include 'comment_delete.html' %}             <!-- new -->
</div>
```

Create `comment_delete.html`:

``` { .html }
{% block content %}
    <form
        method="post"
        action="{% url 'comment_delete' slug_uuid=article.slug_uuid pk=comment.pk %}"
        class="mod-options"
    >
        {% csrf_token %}
        <button
            style="background: none;
                   border: none;
                   padding: 0;
                   margin: 0;
                   font-size: inherit;
                   margin-left: 5px;
                   opacity: 0.6;
                   cursor: pointer;"
            value="DELETE"
            class="ion-trash-a"
        ></button>
    </form>
{% endblock %}
```

