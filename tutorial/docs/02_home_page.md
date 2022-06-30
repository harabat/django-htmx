# Home page

## Introduction

In this chapter, we'll bring an MVP of our app online: it'll have a
landing page, some articles, and even a navbar! To achieve this, we will
need to write our first view, templates, and URLs.

## Home view

Up to now, <http://127.0.0.1:8000/> still shows the rocket celebrating a
successful install, but what we want is to see our own app.

In *Conduit*, the default view that the unauthenticated user sees on the
home page is the “global feed”, or the list of all articles. That's what
we need to implement.

In `articles/views.py`, we add the following:

``` { .python }
from django.views.generic import ListView

from .models import Article


class Home(ListView):
    """View all published articles for the global feed."""

    queryset = Article.objects.order_by("-created_at")
    context_object_name = "articles"
```

Step by step:

-   The [`ListView` generic display
    view](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#listview)
    displays list of objects: the *Django Girls* tutorial only presents
    Function-Based Views, which are arguably a more intuitive option,
    but [Class-Based
    Views](https://docs.djangoproject.com/en/4.0/topics/class-based-views/)
    (or CBVs) are considered to be best practice, at least according to
    *Two Scoops of Django*, and simplify a *lot* of work
-   the `queryset` attribute (which is shorthand for the `get_queryset`
    method) allows us to [filter the list of
    objects](https://docs.djangoproject.com/en/4.0/topics/class-based-views/generic-display/#viewing-subsets-of-objects)
    returned by `ListView` the way we need (here, we order them from
    most to least recent), while the default would be to simply specify
    `model = Article` and get `Article.objects.all()`
-   the `context_object_name` attribute provides a [human-friendly name
    for the
    context](https://docs.djangoproject.com/en/4.0/topics/class-based-views/generic-display/#making-friendly-template-contexts)
    for us to use in the template (by default, the context would be
    stored in a variable named `object_list`).

## Home URL

If you followed any previous tutorial, you will remember that, in order
to display a view, we need to specify what URL it corresponds to.

To keep our app logic clear, we will be keeping everything segregated
across our apps: since we want to implement a view of the list of all
articles, we will specify the URLs in our `articles` folder.

Let's create a `articles/urls.py`, and add the following:

``` { .python }
from django.urls import path

from .views import Home

urlpatterns = [
    path("", Home.as_view(), name="home"),
]
```

We're telling our `Articles` app that the root URL
(<http://127.0.0.1:8000/>) should return the view `Home` that we created
in the previous section.

However, Django doesn't know to look into `articles/urls.py`: it is only
aware of the default `urls.py` file created earlier in the previous
chapter. We add the following line in `config/urls.py`, so that the
project-level `urls.py` is aware of the app-level URLs defined in
`articles/urls.py`:

``` { .python hl_lines="2 6" }
from django.contrib import admin
from django.urls import path, include                       # new

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("conduit.articles.urls")),             # new
]
```

## Templates and static files

We have a Home view and URL: we need a template now. In keeping with our
commitment to keeping the structure of our project clear and logical, we
will create a single project-wide folder for all templates, and we'll do
the same for static files (icons, CSS, etc.): this kind of code is going
to be heavily shared by both `articles` and `users` apps, so it's better
to have a folder for the whole project than one for each app (all the
more so that our apps are not expected to be plugged into other
projects).

Let's create the `templates` and `static` folders:

``` { .shell }
(django) conduit$ mkdir templates
(django) conduit$ mkdir static
```

We need to modify `config/settings.py` so Django is aware of our
project's architecture.

Let's define the `APPS_DIR` below `BASE_DIR` first: it will point to our
`conduit` folder and will make the next modifications a bit shorter.

``` { .python hl_lines="3" }
# ...
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "conduit"                     # new
```

The [`TEMPLATES`
section](https://docs.djangoproject.com/en/4.0/ref/settings/#templates)
of `config/settings.py` holds the template-related settings: that's
where we need to notify Django about where our templates are.

The `DIRS` setting, which indicates the location of template source
files should point to our new `conduit/templates` folder:

``` { .python hl_lines="5 7" }
TEMPLATES = [
    {
        # ...
        # "DIRS": [],                       # from this
        "DIRS": [APPS_DIR / "templates"],   # to this
    },
]
```

We will also change the [`STATICFILES_DIRS`
setting](https://docs.djangoproject.com/en/4.0/ref/settings/#staticfiles-dirs)
in the static files section of `config/settings.py` so that it points to
our new `conduit/static` folder:

``` { .python hl_lines="3" }
# ...
STATIC_URL = "/static/"
STATICFILES_DIRS = [APPS_DIR / "static"]    # new
```

## Base template

Before we start writing the templates, a few words. As stated in the
introduction, the HTML is adapted from other RealWorld projects: mostly
the [Svelte implementation](https://github.com/sveltejs/realworld/)
(because Svelte is unexpectedly close to Django's templating language),
but we also picked and chose from other projects, both in situations
where the code or the file structure were more in line with what we
needed here, or when the UI of one implementation was better in some
way. However, because we're building the app from scratch (adding
features, changing the UI, etc.), our file structure and code will be
affected. The HTML of the finished *Conduit* app should be almost
identical to any other implementation's HTML (take or leave some
specificities of our chosen frameworks). Because this is not an HTML or
UI tutorial, we won't be explaining the HTML files' structure, the
classes, the CSS, etc. Onwards!

The groundwork is completed: Django knows where to find our templates.
Let's create the base template then.

``` { .shell }
(django) conduit$ touch templates/base.html
```

The `templates/base.html` template, copied from [Svelte's app.html
file](https://github.com/sveltejs/realworld/blob/master/src/app.html),
will contain the following:

``` { .html }
<!DOCTYPE html>
{% load static %}
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link rel="icon" href="{% static '/icons/favicon.ico' %}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- icons for later -->
    <link href="//code.ionicframework.com/ionicons/2.0.1/css/ionicons.min.css" rel="stylesheet" type="text/css">
    <!-- fonts -->
    <link href="//fonts.googleapis.com/css?family=Titillium+Web:700|Source+Serif+Pro:400,700|Merriweather+Sans:400,700|Source+Sans+Pro:400,300,600,700,300italic,400italic,600italic,700italic" rel="stylesheet" type="text/css">
    <!-- Thinkster's CSS -->
    <link rel="stylesheet" href="//demo.productionready.io/main.css">
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

Step by step:

-   the `{% load static %}` tag allows to make available the static
    files located in the `static` folder
-   `{% block title %}` and `{% block content %}` are [`block`
    tags](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#std-templatetag-block)
    and define the parts of the template that will be overridden by
    child templates through Django's [template
    inheritance](https://docs.djangoproject.com/en/4.0/ref/templates/language/#template-inheritance),
    which will be illustrated in the very next section

We also need to download the favicon referenced in our template:
download the file located at the URL below to
`static/icons/favicon.ico`:

<https://github.com/gothinkster/react-redux-realworld-example-app/blob/master/public/favicon.ico>

## Home template

Time to make the `home.html` template: for now it only needs to display
our “global feed”.

Let's create the `templates/home.html` template (based on Svelte's
[index.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/index.svelte)
and
[ArticleList](https://github.com/sveltejs/realworld/blob/master/src/lib/ArticleList/)
templates) and add the following to it:

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
                  <a href="" class="preview-link">
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

A quick explanation:

-   we show the classic *Conduit* banner
-   with an [`if` template
    tag](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#if)
    and the [`length_is` template
    filter](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#length-is)
    we check that our `articles` variable (which we have named with
    `context_object_name = "articles"` in the `Home` view, remember?)
    has at least 1 article:
    -   if there are no articles, we show a message
    -   otherwise, we iterate through the articles with a [`for`
        template
        tag](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#for)
        (the syntax is the same as for a normal Python `for` loop) and
        show a preview:
        -   the preview contains the article's author's username,
            creation date, title, and description
        -   the preview redirects to nothing for now (even though we
            don't have any links to show yet, we need to have a link
            there for CSS reasons)

Let's go to our server and reload the page: surely we can finally
contemplate our glorious creation? No. If you've been following, you
should see the error below:

> TemplateDoesNotExist at /
>
> articles/article_list.html
>
> Request Method: GET Request URL: <http://127.0.0.1:8000/> Django
> Version: 4.0.4 Exception Type: TemplateDoesNotExist Exception Value:
>
> articles/article_list.html

What the error says is that the template is missing, even though we know
that it definitely *is* there. The issue is that Django expects a
template named article_list.html, which is the default template expected
by our `Home` view, which is a `ListView` for the `Article` model. To
fix that, we need to go to `articles/views.py` and add the following:

``` { .python hl_lines="4" }
class Home(ListView):
    """View all published articles for the global feed."""

    template_name = "home.html"                         # new
    queryset = Article.objects.order_by("-created_at")
    context_object_name = "articles"
```

Try reloading again and this is what you should see:

<figure>
<img src="./assets/home - global feed.png" width="600"
alt="Global feed in our app" />
<figcaption aria-hidden="true">Global feed in our app</figcaption>
</figure>

<figure>
<img src="./assets/home - global feed - realworld.png" width="600"
alt="Global feed in the RealWorld app" />
<figcaption aria-hidden="true">Global feed in the RealWorld
app</figcaption>
</figure>

It's starting to look like something! However we can improve the
template a bit.

## Breaking templates into subtemplates

We want to keep our templates as modular as possible, to simplify the
structure of our project and make it easier to think about.

The structure of the Svelte implementation makes a lot of sense and
avoids us having to reinvent the wheel, so we'll take advantage of it.

Specifically, we will copy the Svelte implementation's [ArticleList
structure](https://github.com/sveltejs/realworld/tree/master/src/lib/ArticleList)
by moving the whole `{% if articles|length_is:"0" %}...{% endif %}`
clause HTML out of `templates/home.html` and into two separate files.

In `templates/home.html`, we remove the `if` clause and replace it with
an [`include`
tag](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#include):

``` { .html hl_lines="6" }
<!-- ... -->
<div class="container page">
  <div class="row">
    <div class="col-md-9">
      <!-- {% if articles|length_is:"0" %}...{% endif %} -->    <!-- from this -->
      {% include "article_list.html" %}                         <!-- to this -->
    </div>
  </div>
</div>
```

We create `templates/article_list.html` and add the code that we removed
earlier, except the contents of the `for` clause:

``` { .html hl_lines="9" }
{% if articles|length_is:"0" %}
  <div class="article-preview">
    No articles are here... yet.
  </div>
{% else %}
  <div>
    {% for article in articles %}
      {% include "article_preview.html" %}
    {% endfor %}
  </div>
{% endif %}
```

The `templates/article_preview.html` template will contain the remaining
code:

``` { .html }
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
  <a href="" class="preview-link">
    <h1>{{ article.title }}</h1>
    <p>{{ article.description }}</p>
    <span>Read more...</span>
  </a>
</div>
```

Reload the *Conduit* app to check that everything's still working.

## Navbar

Let's create a simple navigation bar now. Because we have yet to
implement authentication and profiles, the navbar will just contain a
link to `Home`, the page we just finished building.

Let's add the following lines to `templates/base.html`:

``` { .html hl_lines="2" }
<body>
  {% include "nav.html" %}              <!-- new -->
  <main>
    {% block content %}
    {% endblock %}
  </main>
</body>
```

Let's create `templates/nav.html` and add the following to it (copying
Svelte's [Nav.svelte
template](https://github.com/sveltejs/realworld/blob/master/src/lib/Nav.svelte)):

``` { .html }
<nav class="navbar navbar-light">
  <div class="container">
    <a rel="prefetch" class="navbar-brand" href="/">conduit</a>
    <ul class="nav navbar-nav pull-xs-right">
      <li class="nav-item">
        <a href="{% url 'home' %}" rel="prefetch" class="nav-link">
          Home
        </a>
      </li>
    </ul>
  </div>
</nav>
```

The [`url`
tag](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#url)
is new to us: it enables us to specify URLs by name, instead of writing
them every time we need to make a link in our HTML.

In this case, we want our navbar to redirect users to the `Home` view,
which is matched by the URL named `home` (as specified in
`articles/urls.py`).

Try clicking on the link: your page should reload (because you're
redirected to it).

