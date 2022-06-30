# Creating, editing, and deleting Articles

## Introduction

We have implemented the features that allow us to view articles, but up
to now we've been modifying them through the Django admin. We need to
let our users create, edit, and delete articles.

Technically, these functionalities should only be available to logged-in
users, but that's not something we can work on just yet, so we will go
ahead and implement the article features, and modify them later in order
to take into account user authentication.

## Creating Articles

Let's allow users to create articles. The most basic feature possible.

!!! Advice

    We remind you again that up to now we've mostly been keeping to what the
[DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial): if
you're having difficulties following, you should do that tutorial, as
its pace is a bit slower. Unless, of course, the fault is on my side of
the screen, in which case please provide feedback :).

### Subclass a `CreateView`

Creating instances of a model is bound to be a common task, right?
Unsurprisingly, Django has a ready-made class-based view for that.

We subclass a `CreateView` in `articles/views.py`:

``` { .python hl_lines="2 6-11" }
# ...
from django.views.generic import CreateView, DetailView, ListView   # new

# ...

class EditorCreateView(CreateView):                                 # new
    """View for creating articles."""                               #
                                                                    #
    model = Article                                                 #
    fields = ['title', 'description', 'body']                       #
    template_name = "editor.html"                                   #
```

The [`CreateView` class-based
view](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/#createview)
is a generic editing view that “displays a form for creating an object,
redisplaying the form with validation errors (if there are any) and
saving the object”. What more could we want? Sometimes, using
class-based views (and Django in general) might feel like a cheat code,
but it's completely legal, don't worry.

In the code above, we specify the following:

-   the model that we're creating new instances of
-   the template name
-   the fields we want to have available to the user when creating the
    form: specifically, we're leaving out the `author` field here.

### Add a `urlpattern`

We add the following to `articles/urls.py`:

``` { .python }
# ...
from .views import ArticleDetailView, EditorCreateView, Home            # new

urlpatterns = [
    # ...
    path("editor", EditorCreateView.as_view(), name="editor_create"),   # new
]
```

Not much to explain here.

### Create a form

This section will have lots of new elements and information, so take a
break.

We need to create the template `templates/editor.html` (based on Svelte
implementation's
[\_Editor.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/editor/_Editor.svelte)
template):

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

There's a lot here: we've reached the point where we have to implement
forms, a major use case in web dev. While forms are one of Django's many
strong points, there is a lot of new material to understand.

The [Django docs section that deals with
forms](https://docs.djangoproject.com/en/4.0/topics/forms/) says:

> Django handles three distinct parts of the work involved in forms:
>
> -   preparing and restructuring data to make it ready for rendering
> -   creating HTML forms for the data
> -   receiving and processing submitted forms and data from the client

-   `<form method="post">`
    -   Forms allow users to provide input to the website they're
        visiting, that the website can then process and act upon.
    -   We want to modify data server-side (we will create new `Article`
        instances), so we need to make a POST form (which we do with
        `method="post"`).
-   `{% csrf_token %}`
    -   POST forms need to mitigate against [Cross Site Request
        Forgeries](https://docs.djangoproject.com/en/4.0/ref/csrf/), a
        type of malicious attack, but Django makes this very easy: in
        our case, we only need to include the `{% csrf_token %}` tag
        inside the `<form>` element (though you might have to do a bit
        more work [in other
        circumstances](https://docs.djangoproject.com/en/4.0/howto/csrf/using-csrf)).
-   `{{ form.non_field_errors }}`
    -   The `{{ form.non_field_errors }}` variable will display any
        errors that are not field-specific, which is why this variable
        is outside of any fieldsets.
-   

There are different ways to render a form: it depends on whether
[Django's defaults unpacking of form
fields](https://docs.djangoproject.com/en/4.0/topics/forms/#form-rendering-options)
is sufficient, whether you need more [flexibility in how you render the
fields](https://docs.djangoproject.com/en/4.0/topics/forms/#rendering-fields-manually).
We want a lot of flexibility (we want the fields to be in a specific
order, to how distinct placeholder values).

### Add a navbar button

We add a `New article` button to the Nav bar in `templates/nav.html`
(still copying Svelte's [Nav.svelte
template](https://github.com/sveltejs/realworld/blob/master/src/lib/Nav.svelte)):

``` { .html hl_lines="4 5-10 14-23" }
<!-- ... -->
<ul class="nav navbar-nav pull-xs-right">
  <li class="nav-item">
    {% url 'home' as home %}                                                        <!-- new -->
    <!-- <a href="{% url 'home' %}" rel="prefetch" class="nav-link"> -->            <!-- from this -->
    <a                                                                              <!-- to this -->
      href="{{ home }}"                                                             <!-- # -->
      rel="prefetch"                                                                <!-- # -->
      class="nav-link {% if request.path == home %}active{% endif %}"               <!-- # -->
    >                                                                               <!-- # -->
      Home
    </a>
  </li>
  <li class="nav-item">                                                             <!-- new -->
    {% url 'editor_create' as editor_create %}                                      <!-- # -->
    <a                                                                              <!-- # -->
      href="{{ editor_create }}"                                                    <!-- # -->
      rel="prefetch"                                                                <!-- # -->
      class="nav-link {% if request.path == editor_create %}active{% endif %}"      <!-- # -->
    >                                                                               <!-- # -->
      <span class="ion-compose"> New Post </span>                                   <!-- # -->
    </a>                                                                            <!-- # -->
  </li>                                                                             <!-- # -->
</ul>
```

We added `{% url 'home' as home %}` and
`class "nav-link {% if request.path == home %}active{% endif %}"` to
better style active links.

### Override `form_valid`

Try to create an article in your app. When you hit “Publish”, you'll get
an error:

> IntegrityError at /editor NOT NULL constraint failed:
> articles_article.author_id

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
        self.object = form.save(commit=False)           #
        self.object.author = self.request.user.profile  #
        self.object.save()                              #
        return super().form_valid(form)                 #
```

Once this is done, try creating another article: it should work.

## Editing Articles

We will now implement the editing feature.

In `views.py`, add the following:

``` { .python }
# ...
from django.views.generic import (
    # ...
    UpdateView,
)

# ...

class EditorUpdateView(UpdateView):
    """edit article"""

    model = Article
    fields = ["title", "description", "title"]
    template_name = "editor.html"
```

We're using the same template for creating and editing articles. In
`urls.py`, add:

``` { .python }
# ...
from .views import (
    # ...
    EditorUpdateView
)

urlpatterns = [
    # ...
    path("editor/<slug:slug_uuid>", EditorUpdateView.as_view(), name="editor_update"),
]
```

In `article_detail.html`, we add a button for editing the article and
pass `article.slug_uuid` as an argument to the url (see [the
documentation for `url`
tag](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#url)),
given that our URL expects a `slug_uuid` (`editor/<slug:slug_uuid>`).
The documentation for ):

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
            href="{% url 'editor_update' slug_uuid=article.slug_uuid %}"
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

``` { .html hl_lines="8 17 26" }
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
# ...
from django.views.generic import (
    # ...
    DeleteView,
)
from django.urls import reverse_lazy

# ...
class EditorDeleteView(DeleteView):
    """delete article"""

    model = Article
    success_url = reverse_lazy("home")
    template_name = "article_detail.html"
```

Notice that we're using the `article_detail.html` template. We could use
a separate one, but that would require to load a new page, which seems
unnecessary: we'll see in a second how we're making this work.

In `urls.py`:

``` { .python }
# ...
from .views import (
    # ...
    EditorDeleteView,
)

urlpatterns = [
    # ...
    path("editor/<slug:slug_uuid>/delete", EditorDeleteView.as_view(), name="editor_delete"),
]
```

Now, create an `article_delete.html` file: this will hold the form for
deleteing the article.

``` { .html }
<form
    method="POST"
    action="{% url 'editor_delete' slug_uuid=article.slug_uuid %}"
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
        href="{% url 'editor_update' slug_uuid=article.slug_uuid %}"
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

