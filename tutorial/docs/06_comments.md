# Comments

## Introduction

Now that we have articles, we need comments. Gotta give our users a voice, right?

## Model

Comments are a whole new object for our app, so we need to create a model.

A comment will need a related article, an author, a body, and a date.

Let's create a `Comment` model in `articles/models.py`:

``` { .python  }
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
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:60] + "..."

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.article.slug_uuid})
```

We've been through this before, so we can be quick:

- Our `article` field is a many-to-one relationship that relates the `Comment` model to the `Article` model. By default, Django uses the `pk` of the related object, but we're working with `slug_uuid` fields in this tutorial, hence `to_field="slug_uuid"`.
- The `author` is a many-to-one relationship that relates `Comment` to `Profile`.
- The string representation of our model (`__str__`) is the truncated comment body.
- The canonical URL for a `Comment` instance is the same as the URL for the `Article` instance attached to the comment: we don't need to navigate to specific comments in *Conduit*, so we might as well have a simplified `get_absolute_url`.

Time to `makemigrations` and `migrate`. You should get the following error:

> SystemCheckError: System check identified some issues:
>
> ERRORS: articles.Comment.article: (fields.E311) ‘Article.slug_uuid’ must be unique because it is referenced by a foreign key. HINT: Add unique=True to this field or add a UniqueConstraint (without condition) in the model Meta.constraints.

That's because we're using articles' `slug_uuid` fields as ForeignKeys for the comments (so that we can filter our comments by the attached articles' `slug_uuid` fields instead of their UUIDs). As the error message indicates, this error is easily corrected by adding `unique=True` as an argument to the `slug_uuid` field in the `Article` model in `articles/models.py`.

``` { .python hl_lines="5-6" }
# ...

class Article(models.Model):
    # ...
    # slug_uuid = models.SlugField(max_length=100, editable=False)                  # from this
    slug_uuid = models.SlugField(max_length=100, editable=False, unique=True)       # to this
    # ...
```

You should be able to `makemigrations` and `migrate` after that.

``` shell
(django) django_tutorial$ python manage.py makemigrations
# Migrations for 'articles':
#   conduit/articles/migrations/0004_alter_article_slug_uuid_comment.py
#     - Alter field slug_uuid on article
#     - Create model Comment
(django) django_tutorial$ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, articles, auth, contenttypes, sessions, users
# Running migrations:
#   Applying articles.0004_alter_article_slug_uuid_comment... OK
```

Now, we need to register our model in `articles/admin.py`, so that we can access that object in the Django admin:

``` { .python hl_lines="2 5" }
from django.contrib import admin
from .models import Article, Comment        # new

admin.site.register(Article)
admin.site.register(Comment)                # new
```

## Viewing comments

In order to view comments, we need to have some comments to view first: go to the Django admin and create a few comments for a couple articles by hand.

We want to be able to view the comments on each article's detail page. Consequently, we need to modify `templates/article_detail.html` (based on Svelte implementation's \[\[<https://github.com/sveltejs/realworld/blob/master/src/routes/article/%5Bslug%5D/index.svelte>\]\[article/\[slug\]/index.svelte\]\]):

``` { .html hl_lines="10-13" }
<!-- ... -->
<div class="container page">
  <div class="row article-content">
    <div class="col-xs-12">
      <div>
        {{ article.body|linebreaks }}
      </div>
    </div>
  </div>
  <hr />                                    <!-- new -->
  <div class="row">                         <!-- new -->
    {% include "comment_container.html" %}  <!-- new -->
  </div>                                    <!-- new -->
</div>
<!-- ... -->
```

Now create `templates/comment_container.html` and add the following (based on Svelte implementation's \[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\slug\\/\_CommentContainer.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_CommentContainer.svelte)\]\[\_CommentContainer.svelte\]\]):

``` { .html  }
<div class="col-xs-12 col-md-8 offset-md-2">
  {% for comment in article.comments.all|dictsortreversed:'created_at' %}
    {% include "comment.html" %}
  {% endfor %}
</div>
```

We want to view all the comments for the article we're viewing, from most to least recent (which we achieve with the [`dictsortreversed` template filter](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#dictsortreversed)).

We will implement the rendering logic for our comments in `templates/comment.html` (based on Svelte implementation's \[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\slug\\/\_Comment.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_Comment.svelte)\]\[\_Comment.svelte\]\]):

``` { .html  }
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
```

Nothing new here: this template displays the comment's body, author's username, and creation date.

Try navigating to one of the articles that you created comments for through the Django admin: you should see them displayed under the article (though they made do with some decoration, which we will get to later).

## Creating comments

We will now start allowing our users to leave comments on the website.

We could do this like in the Django Girls tutorial: the `ArticleDetailView` would include a button that would direct to `CommentCreateView` on a separate page, and saving the comment would bring the user back to the `ArticleDetailView`. However, the `RealWorldApp` allows users to create and save their comments directly below the article, on the same page, so that's what we're going to try.

Surprisingly, this is not straightforward to implement in Django, because it implies mixing `DetailView` and `CreateView` functionalities in a single page, which is made difficult by the fact that the `DetailView` doesn't have a POST method, while the `CreateView` requires it.

### Create `CommentCreateView`

Fortunately, our use case is [covered in the Django documentation](https://docs.djangoproject.com/en/5.0/topics/class-based-views/mixins/#an-alternative-better-solution), which greatly simplifies the task at hand.

First, we'll create a `CommentCreateView` in `users/views.py`:

``` { .python  }
# ...
from django.urls import reverse_lazy, reverse
from .models import Article, Comment

# ...
class CommentCreateView(CreateView):
    """View for creating comments."""

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
        return reverse(
            "article_detail", kwargs={"slug_uuid": self.object.article.slug_uuid}
        )
```

We have seen a lot of this before, but a lot is new:

- We subclass a `CreateView` and specify the object this view will be related to (`Comment`), which fields we want to be able to modify when we create `Comment` instances (we only want to modify the comment body), and which template our view is going to be using.
- We override the `form_valid` method because we need to specify the `author` (the currently logged-in user) and `article` (the article that the comment is being attached to) fields required by the `Comment` model.
- We also override the `get_success_url` because we want the user to be redirected to the `ArticleDetailView` upon saving the comment (we need to import the `reverse` URL resolver for that).

### Adapt `ArticleDetailView`

Now, we need to modify the `ArticleDetailView` to make the `CommentCreateView`'s form available to `templates/article_detail.html` through the `get_context_data` method:

``` { .python hl_lines="8-11" }
# ...

class ArticleDetailView(DetailView):
    """Detail view for individual articles."""

    # ...

    def get_context_data(self, **kwargs):                       # new
        context = super().get_context_data(**kwargs)            # new
        context["form"] = CommentCreateView().get_form_class()  # new
        return context                                          # new
```

Let's explain our override of `get_context_data`:

- the [`get_context_data` method](https://docs.djangoproject.com/en/5.0/ref/class-based-views/mixins-simple/#django.views.generic.base.ContextMixin.get_context_data) populates the dictionary that will be used as the template context
- `super().get_context_data(**kwargs)` is boilerplate that populates our `context` with the data the view would come with by default
- we then pass the newly created `CommentCreateView`'s form (which we get through its [`get_form_class` method](https://docs.djangoproject.com/en/5.0/ref/class-based-views/mixins-editing/#django.views.generic.edit.FormMixin.get_form_class)) to the `ArticleDetailView`'s `context` (`DetailView` generic views do not have a `form`, so we're not overwriting anything here)
- we now have access to the relevant context of both our views.

### Combine `ArticleDetailView` and `CommentCreateView`

Finally, we create a view that combines `ArticleDetailView` and `CommentCreateView`:

``` { .python  }
# ...
from django.views.generic import (
    # ...
    View,
)


# ...
class ArticleCommentView(View):
    """View for viewing articles and posting comments."""

    def get(self, request, *args, **kwargs):
        view = ArticleDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)
```

We now have a new hybrid view that, depending on whether the method is `GET` or `POST`, will return the `ArticleDetailView` or the `CommentCreateView`, respectively.

### Adapt the `urlpattern`

In order for our new hybrid view to be able to act as intended, we need to specify it as the view that deals with requests to the `article/<slug:slug_uuid>` path in `articles/urls.py`:

``` { .python hl_lines="4-5 11-12" }
# ...
from .views import (
    # ...
    # ArticleDetailView,                                                                    # from this
    ArticleCommentView,                                                                     # to this
)

urlpatterns = [
    # ...
    path(
        # "article/<slug:slug_uuid>", ArticleDetailView.as_view(), name="article_detail"    # from this
        "article/<slug:slug_uuid>", ArticleCommentView.as_view(), name="article_detail"     # to this
    ),
]
```

### Create a template

Now that `articles/views.py` and `articles/urls.py` are ready, we need to create the templates.

Create `comment_input.html` (based on Svelte implementation's \[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\slug\\/\_CommentInput.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_CommentInput.svelte)\]\[\_CommentInput.svelte\]\]):

``` { .html  }
<form
    method="post"
    action="{% url 'article_detail' slug_uuid=object.slug_uuid %}"
    class="card comment-form"
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
```

This POST form corresponds to `CommentCreateView`'s form: when we send submit this form in our app, the `ArticleCommentView` will return the `CommentCreateView`, which will process the request and create the requested `Comment` instance.

In `templates/comment_container.html`, we include the `comment_input.html` template:

``` { .html hl_lines="2-4" }
<div class="col-xs-12 col-md-8 offset-md-2">
  <div>                                                             <!-- new -->
    {% include "comment_input.html" %}                              <!-- # -->
  </div>                                                            <!-- # -->
  {% for comment in article.comments.all|dictsortreversed:'created_at' %}
<!-- ... -->
```

Everything should be working now. Try to create some comments on an article.

## Deleting comments

We now want to be able to delete comments.

In `articles/views.py`, add `CommentDeleteView`:

``` { .python  }
# ...

class CommentDeleteView(DeleteView):
    """View for deleting comments."""

    model = Comment
    template_name = "article_detail.html"

    def get_success_url(self):
        return reverse("article_detail", kwargs={"slug_uuid": self.object.article.slug_uuid})
```

In `articles/urls.py`, we add a `urlpattern`:

``` { .python  }
urlpatterns = [
    # ...
    path(
        "article/<slug:slug_uuid>/comment/<int:pk>/delete",
        CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
```

We require `pk` as an argument because `CommentDeleteView` needs this information to identify the comment to delete. The `<slug:slug_uuid>` part is unnecessary, but it makes the path more logical, I find.

Create `templates/comment_delete.html` (based on Svelte implementation's \[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\slug\\/\_Comment.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_Comment.svelte)\]\[\_Comment.svelte\]\]):

``` { .html  }
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
```

In `templates/comment.html`:

``` { .html hl_lines="9" }
<!-- ... -->
<div class="card-footer">
  <span class="comment-author">
    {{ comment.author }}
  </span>
  <span class="date-posted">
    {{ comment.created_at|date:"D M d Y" }}
  </span>
  {% include 'comment_delete.html' %}             <!-- new -->
</div>
<!-- ... -->
```

