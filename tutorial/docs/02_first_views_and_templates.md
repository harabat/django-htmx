# First views and templates

## Article model

We'll start by making a model for our articles in `articles/models.py`.
The articles need a title, a body (the text), a description, an author,
and a creation date.

``` { .python }
from django.db import models


class Article(models.Model):
    title = models.CharField(db_index=True, max_length=255)
    description = models.TextField(max_length=2000)
    body = models.TextField()
    author = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})
```

The `ForeignKey` allows us to have multiple articles for every user.
`on_delete=models.CASCADE` means that the article will be deleted if the
user is deleted. `related_name="articles"` allows us to access a user's
articles through an `articles` attribute.

Let's sync the database again:

``` { .shell }
(django) django_tutorial$ python manage.py makemigrations
(django) django_tutorial$ python manage.py migrate
```

## Django admin

In order to have something to work with for the rest of the tutorial, we
need to create some posts. Because we can't yet do it through Conduit,
we will do so through Django admin.

First, register the `Article` model in `articles/admin.py` by adding the
following line:

``` { .python hl_lines="4" }
from django.contrib import admin
from .models import Article

admin.site.register(Article)            # new
```

The server should still be running (otherwise restart it). Log in as the
superuser you just created and create 3 articles.

## Home view

The default view that the unauthenticated user has is the global feed,
or the list of all articles.

We add the following line in `django_tutorial/conduit/urls.py`, so that
the project-level `urls.py` is aware of the urls defined in
`articles/urls.py`:

``` { .python hl_lines="6" }
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('conduit.articles.urls')),                         #new
]
```

Let's create a `urls.py` file in the `articles` folder, and add the
following:

``` { .python }
from django.urls import path
from . import views

urlpatterns = [path("", Home.as_view(), name="home")]
```

In `views.py`, we add the following:

``` { .python }
from .models import Article


class Home(TemplateView):
    """all published articles"""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.order_by("-created_at")
        return context
```

## Templates folder

We need a template now, but before this we need to create a folder for
templates and for static files (icons, CSS, etc.).

It's easier to have all templates in one place, instead of in each
separate app, and the same is true for static files. Let's create the
`templates` and `static` folders:

``` { .shell }
(django) conduit$ mkdir templates
(django) conduit$ mkdir static
```

We need to modify `settings.py` so Django is aware of our project's
architecture. Let's define the APPS_DIR below BASE_DIR first:

``` { .python }
# ...
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "conduit"
```

Let's change the `DIRS` line in the `TEMPLATES` section in `settings.py`
like this:

``` { .python }
# ...
"DIRS": [APPS_DIR / "templates"], # changed from "DIRS": []
```

Similarly, let's define the `STATIC_ROOT` directory below the `STATIC`
line like this:

``` { .python }
# ...
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [APPS_DIR / "static"]
```

## Base template

Let's create the base template now.

``` { .shell }
(django) conduit$ touch templates/base.html
```

This template will contain the following:

``` { .html }
<!doctype html>
{% load static %}
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="{%  static '/icons/favicon.ico' %}">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- favicon -->
        <!-- Thinkster's CSS -->
        <link rel="stylesheet" href="//demo.productionready.io/main.css">
        <!-- icons for later -->
        <link href="//code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css" rel="stylesheet" type="text/css">
        <!-- fonts -->
        <link href="//fonts.googleapis.com/css?family=Titillium+Web:700|Source+Serif+Pro:400,700|Merriweather+Sans:400,700|Source+Sans+Pro:400,300,600,700,300italic,400italic,600italic,700italic&display=swap" rel="stylesheet" type="text/css">
        {% block title %}
            <title>Conduit: Django + HTMX</title>
        {% endblock %}
    </head>
    <body>
        <main>
            {% block content %}
            {% endblock %}
        </main>
    </body>
</html>
```

We'll also download the favicon referenced in our template: download the
file located at the URL below to
`conduit/articles/static/icons/favicon.ico`:
<https://github.com/gothinkster/react-redux-realworld-example-app/blob/master/public/favicon.ico>

## Home template

Now we'll make the `home.html` template, which for now only needs to
display our “global feed”.

Let's create the template and add the following to it:

``` { .html }
{% extends 'base.html' %}
{% block content %}
  <div class="home-page">
    <div class="banner">
      <div class="container">
        <h1 class="logo-font">conduit</h1>
        <p>A place to share your knowledge.</p>
      </div>
    </div>
    <div class="container page">
      <div class="row">
        <div class="col-md-9">
          {% if articles|length_is:"0" %}
            <div class="article-preview">
              No articles are here... yet.
            </div>
          {% else %}
            <div>
              {% for article in articles %}
                <div class="article-preview">
                  <div class="article-meta">
                    <div class="info">
                      <span class="author">
                        {{ article.author.user.username }}
                      </span>
                      <span class="date">
                        {{ article.created_at|date:"D M d Y" }}
                      </span>
                    </div>
                  </div>
                  <a href="{{ article.get_absolute_url }}" rel="prefetch" class="preview-link">
                    <h1>{{ article.title }}</h1>
                    <p>{{ article.description }}</p>
                    <span>Read more...</span>
                  </a>
                </div>
              {% endfor %}
            </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```

The HTML is adapted from other realworld projects (especially the
[SvelteKit implementation of the RealWorld
app](https://github.com/sveltejs/realworld/), because Svelte is
unexpectedly close to Django's templating language). Because the HTML is
little more than a copy-paste, we won't explain its structure and
classes: suffice it to say that this is required to have something that
looks like the actual Realworld app.

<figure>
<img src="../assets/home - global feed.png" width="600" alt="Global feed in our app" /><figcaption aria-hidden="true">Global feed in our app</figcaption>
</figure>

<figure>
<img src="../assets/home - global feed - realworld.png" width="600" alt="Global feed in the RealWorld app" /><figcaption aria-hidden="true">Global feed in the RealWorld app</figcaption>
</figure>

It's starting to look like something, but we can improve the template a
bit.

We want to keep our templates as modular as possible, to simplify the
structure of our project and make it easier to think about. In this
case, we could move the `<div class="article-preview">` to a separate
file. Let's move all the code in the `{% for article in articles %}` for
loop into the file `article_preview.html` (which we need to create).

In `templates/home.html`, we change the following lines:

``` { .html hl_lines="4" }
<div class="container page">
  <div class="row">
    <div class="col-md-9">
      {% include 'article_list.html' %}  <!-- from {% if articles|length%}...{% end%} -->
    </div>
  </div>
</div>
```

Our `templates/article_list.html` file should look like this:

``` { .html hl_lines="9" }
{% block content %}
  {% if articles|length_is:"0" %}
    <div class="article-preview">
      No articles are here... yet.
    </div>
  {% else %}
    <div>
      {% for article in articles %}
        {% include 'article_preview.html' %} <!-- from <div class="article-preview">...</div>-->
      {% endfor %}
    </div>
  {% endif %}
{% endblock %}
```

The `templates/article_preview.html` file should look like this:

``` { .html }
{% block content %}
  <div class="article-preview">
    <div class="article-meta">
      <div class="info">
        <span class="author">
          {{ article.author.user.username }}
        </span>
        <span class="date">
          {{ article.created_at|date:"D M d Y" }}
        </span>
      </div>
    </div>
    <a href="{{ article.get_absolute_url }}" rel="prefetch" class="preview-link">
      <h1>{{ article.title }}</h1>
      <p>{{ article.description }}</p>
      <span>Read more...</span>
    </a>
  </div>
{% endblock %}
```

You might wonder why we're adopting this template structure: it actually
comes from the Svelte implementation of the RealWorld app, and, since it
makes a lot of sense and avoids us having to reinvent the wheel, we are
taking advantage of it.

## Navbar

Let's create a simple navigation bar. Because we have yet to implement
authentication and profiles, the navbar will just contain a link to
`Home`.

Let's add the following lines to `base.html`:

``` { .html hl_lines="2" }
<body>
    {% include 'nav.html' %}            <!-- new -->
    <main>
        {% block content %}
        {% endblock %}
    </main>
```

Let's create `nav.html` in our `templates` folder and add the following
to it:

``` { .html }
<nav class="navbar navbar-light">
  <div class="container">
    <a rel="prefetch" class="navbar-brand" href="/">conduit</a>
    <ul class="nav navbar-nav pull-xs-right">
      <li class="nav-item">
        <a
          href="{% url 'home' %}"
          rel="prefetch"
          class="nav-link"
        >
          Home
        </a>
      </li>
    </ul>
  </div>
</nav>
```

