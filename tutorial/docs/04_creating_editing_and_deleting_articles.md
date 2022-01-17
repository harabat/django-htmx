# Creating, editing, and deleting Articles

We have implemented the features that allow to view articles, but we
need to allow users to create, edit, and delete them as well. We'll
first implement this functionality, and modify it later to take into
account user authentication.

## Creating Articles

Let's allow users to create articles.

We define the `EditorCreateView` view in `views.py`:

``` { .python }
# other imports
from django.views.generic import (
     # other views
     CreateView
)

# other views

class EditorCreateView(CreateView):
    """create article"""

    model = Article
    fields = ['title', 'description', 'body']
    template_name = "editor.html"
```

We add the following to `urls.py`:

``` { .python }
# other imports
from .views import Home, ArticleDetailView, EditorCreateView

urlpatterns = [
    # other paths
    path("editor", EditorCreateView.as_view(), name="editor_create"),
]
```

We add a `New article` button to the Nav bar in `nav.html`:

``` { .html hl_lines="3, 6, 8, 13-23" }
<ul class="nav navbar-nav pull-xs-right">
  <li class="nav-item">
    {% url 'home' as home %}                                    <!-- new -->
    <a
      href="{{ home }}"                                         <!-- new -->
      rel="prefetch"
      class="nav-link
             {% if request.path == home %}active{% endif %}"    <!-- new -->
    >
      Home
    </a>
  </li>
  <li class="nav-item">                                         <!-- new from here -->
    {% url 'editor_create' as editor_create %}
    <a
      href="{{ editor_create }}"
      rel="prefetch"
      class="nav-link
             {% if request.path == editor_create %}active{% endif %}"
    >
      <span class="ion-compose"> New Post </span>
    </a>
  </li>                                                         <!-- new to here -->
</ul>
```

We added `{% url 'home' as home %}` and
`class "nav-link {% if request.path == home %}active{% endif %}"` to
better style active links.

Now, we can create the template `editor.html`:

``` { .html }
{% extends 'base.html' %}
{% block title %}
    <title>Editor - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
    <div class="editor-page">
        <div class="container page">
            <div class="row">
                <div class="col-md-10 offset-md-1 col-xs-12">
                    <form method="post">
                        {% csrf_token %}
                        {{ form.non_field_errors }}
                        <fieldset>
                            {% form.non_field_errors %}
                            <fieldset class="form-group">
                                <input
                                    class="form-control form-control-lg"
                                    type="text"
                                    placeholder="Article Title"
                                    name="title"
                                />
                            </fieldset>
                            {{ form.title.errors }}
                            <fieldset class="form-group">
                                <input
                                    class="form-control"
                                    type="text"
                                    placeholder="What's this article about?"
                                    name="description"
                                />
                            </fieldset>
                            {{ form.description.errors }}
                            <fieldset class="form-group">
                                <textarea
                                    class="form-control"
                                    rows="8"
                                    placeholder="Write your article (in markdown)"
                                    name='body'
                                ></textarea>
                            </fieldset>
                            {{ form.body.errors }}
                            <button class="btn btn-lg pull-xs-right btn-primary">
                                Publish Article
                            </button>
                        </fieldset>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

Try to create an article in your app. When you hit “Publish”, you'll get
an error:

```
IntegrityError at /editor
NOT NULL constraint failed: articles_article.author_id
```

That's because the form doesn't know who the author is, and author is a
required field in our model. Let's override the `EditorCreateView`
view's `form_valid` method in our `views.py` file: before we save the
form, we'll set the logged in user (`admin`, for now) as the `author`:

``` { .python hl_lines="8-12" }
class EditorCreateView(CreateView):
    """create article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):                         # new
        self.object = form.save(commit=False)           # new
        self.object.author = self.request.user.profile  # new
        self.object.save()                              # new
        return super().form_valid(form)                 # new
```

Once this is done, try creating another article: it should work.

## Editing Articles

We will now implement the editing feature.

In `views.py`, add the following:

``` { .python }
# other imports
from django.views.generic import (
    # other views
    UpdateView,
)

# other views

class EditorUpdateView(UpdateView):
    """edit article"""

    model = Article
    fields = ["title", "description", "title"]
    template_name = "editor.html"
```

We're using the same template for creating and editing articles. In
`urls.py`, add:

``` { .python }
# other imports
from .views import (
    # other views
    EditorUpdateView
)

urlpatterns = [
    # other paths
    path("editor/<slug:slug>", EditorUpdateView.as_view(), name="editor_update"),
]
```

In `article_detail.html`, we add a button for editing the article and
pass `article.slug` as an argument to the url (see [the documentation
for `url`
tag](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#url)),
given that our URL expects a slug (`editor/<slug:slug>`). The
documentation for ):

``` { .html hl_lines="10-19" }
<div class="article-meta">
    <div class="info">
        <span class="author">
            {{ article.author }}
        </span>
        <span class="date">
            {{ article.created_at|date:"F d, Y" }}
        </span>
    </div>
    <span>                                                              <!-- new from here -->
        <a
            href="{% url 'editor_update' slug=article.slug %}"
            class="btn btn-outline-secondary btn-sm"
        >
            <span class="ion-edit">
                Edit Article
            </span>
        </a>
    </span>                                                             <!-- new to here -->
</div>
```

In the `editor.html` template, we want to have the form fields
prepopulated with the relevant values. When using `UpdateView`, we have
access to the object being updated. Let's add the following to the
`editor.html` template:

``` { .html hl_lines="8, 17, 26" }
<fieldset>
    <fieldset class="form-group">
        <input
            class="form-control form-control-lg"
            type="text"
            placeholder="Article Title"
            name="title"
            value="{{ article.title|default_if_none:'' }}"          <!-- new -->
        />
    </fieldset>
    <fieldset class="form-group">
        <input
            class="form-control"
            type="text"
            placeholder="What's this article about?"
            name="description"
            value="{{ article.description|default_if_none:'' }}"    <!-- new -->
        />
    </fieldset>
    <fieldset class="form-group">
        <textarea
            class="form-control"
            rows="8"
            placeholder="Write your article (in markdown)"
            name="body"
        />{{ article.body|default_if_none:'' }}</textarea>          <!-- new -->
    </fieldset>
    <button class="btn btn-lg pull-xs-right btn-primary">
        Publish Article
    </button>
</fieldset>
```

Try editing an article: all the values should be prepopulated.

## Deleting Articles

In `views.py`, we create a `ArticleDeleteView`:

``` { .python }
# other imports
from django.views.generic import (
    # other views
    DeleteView,
)
from django.urls import reverse_lazy

# other classes
class EditorDeleteView(DeleteView):
    """delete article"""

    model = Article
    success_url = reverse_lazy("home")
    template_name = "article_detail.html"
```

Notice that we're using the `article_detail.html` template. We could use
a separate one, but that would require to load a new page, which seems
unnecessary: we'll in a second how we're making this work.

In `urls.py`:

``` { .python }
# other imports
from .views import (
    # other views
    EditorDeleteView,
)

urlpatterns = [
    # other paths
    path("editor/<slug:slug>/delete", EditorDeleteView.as_view(), name="editor_delete"),
]
```

Now, create an `article_delete.html` file: this will hold the form for
deleteing the article.

``` { .html }
<form
    method="POST"
    action="{% url 'editor_delete' slug=article.slug %}"
    style="display:inline"
>
    {% csrf_token %}
    <button
        class="btn btn-outline-danger btn-sm"
        value="DELETE"
        onclick="return confirm('Are you sure you want to delete {{ article.title }}?')"
    >
        <span class="ion-trash-a">
            Delete Article
        </span>
    </button>
</form>
```

Now, we want to load this template in `article_detail.html` directly,
which we achieve with an `include` tag:

``` { .html hl_lines="10" }
<span>
    <a
        href="{% url 'editor_update' slug=article.slug %}"
        class="btn btn-outline-secondary btn-sm"
    >
        <i class="ion-edit">
            Edit Article
        </i>
    </a>
    {% include 'article_delete.html' %}             <!-- new -->
</span>
```

Try deleting an article: you should get a nice confirmation message
while still on the `article_detail.html` template, before the article is
deleted.

