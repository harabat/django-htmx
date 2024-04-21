# Creating, editing, and deleting Articles

## Introduction

We have implemented the features that allow us to view articles, but up to now we've been modifying them through the Django admin. We need to let our users create, edit, and delete articles.

Technically, these functionalities should only be available to logged-in users, but that's not something we can work on just yet, so we will go ahead and implement the article features, and modify them later in order to take into account user authentication.

## Creating articles

Let's allow users to create articles. The most basic feature possible.

!!! Advice

    We remind you again that up to now we've mostly been keeping to the [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial): if you're having difficulties following, you should do that tutorial instead, as its pace is a bit slower. Unless, of course, the fault is on my side of the screen, in which case please provide feedback :).

### Subclass a `CreateView`

Creating instances of a model is bound to be a common task, right? Unsurprisingly, Django has a ready-made class-based view for that.

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

The [`CreateView` class-based view](https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/#createview) is a generic editing view that “displays a form for creating an object, redisplaying the form with validation errors (if there are any) and saving the object”. What more could we want? Sometimes, using class-based views (and Django in general) might feel like a cheat code, but it's completely legal, don't worry.

In the code above, we specify the following:

- the model that we're creating new instances of
- the template name
- the fields we want to have available to the user when creating the form: specifically, we're leaving out the `author` field here.

### Add a `urlpattern`

We add the following to `articles/urls.py`:

``` { .python  }
# ...
from .views import ArticleDetailView, EditorCreateView, Home            # new

urlpatterns = [
    # ...
    path("editor", EditorCreateView.as_view(), name="editor_create"),   # new
]
```

Not much to explain here.

### Create a form

This section will have lots of new elements and information, so take a break.

We need to create the template `templates/editor.html` (based on Svelte implementation's [\_Editor.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/editor/_Editor.svelte) template):

``` { .html  }
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
            <fieldset>
              {{ form.non_field_errors }}
              <fieldset class="form-group">
                <input
                  class="form-control form-control-lg"
                  type="text"
                  placeholder="Article Title"
                  name="{{ form.title.name }}"
                />
              </fieldset>
              {{ form.title.errors }}
              <fieldset class="form-group">
                <input
                  class="form-control"
                  type="text"
                  placeholder="What's this article about?"
                  name="{{ form.description.name }}"
                />
              </fieldset>
              {{ form.description.errors }}
              <fieldset class="form-group">
                <textarea
                  class="form-control"
                  rows="8"
                  placeholder="Write your article (in markdown)"
                  name="{{ form.body.name }}"
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

There's a lot here: we've reached the point where we have to implement forms, a major use case in web dev. While forms are one of Django's many strong points, there is a lot of new material to understand.

The [Django docs section that deals with forms](https://docs.djangoproject.com/en/5.0/topics/forms/) says:

> Django handles three distinct parts of the work involved in forms:
>
> - preparing and restructuring data to make it ready for rendering
> - creating HTML forms for the data
> - receiving and processing submitted forms and data from the client

Forms allow users to provide input to the website they're visiting, that the website can then process and act upon.

We want to modify data server-side (we will create new `Article` instances), so we need to make a POST form (which we do with `method="post"`).

POST forms need to mitigate against [Cross Site Request Forgeries](https://docs.djangoproject.com/en/5.0/ref/csrf/), a type of malicious attack, but Django makes this very easy: in our case, we only need to include the `{% csrf_token %}` tag inside the `<form>` element (though you might have to do a bit more work [in other circumstances](https://docs.djangoproject.com/en/5.0/howto/csrf/using-csrf)).

There are different ways to render a form: it depends on whether [Django's defaults unpacking of form fields](https://docs.djangoproject.com/en/5.0/topics/forms/#form-rendering-options) is sufficient, or whether you need more [flexibility in how you render the fields](https://docs.djangoproject.com/en/5.0/topics/forms/#rendering-fields-manually). In our case, we want a lot of flexibility: we want the fields to be in a specific order, to have distinct placeholder values, to have different CSS styling, etc., so we'll render them manually.

Because we chose to render form fields manually, we also have to [render form errors manually](https://docs.djangoproject.com/en/5.0/topics/forms/#rendering-form-error-messages). The `{{ form.non_field_errors }}` variable will display any errors that are not field-specific, which is why this variable is outside of any fieldsets. The `{{ form.field_name.errors }}` variables, located in the relevant fieldset tag, will display field-specific errors.

### Add a navbar button

We add a `New article` button to the Nav bar in `templates/nav.html` (still copying Svelte's [Nav.svelte template](https://github.com/sveltejs/realworld/blob/master/src/lib/Nav.svelte)):

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
      <span class="ion-compose">                                                    <!-- # -->
        New Post                                                                    <!-- # -->
      </span>                                                                       <!-- # -->
    </a>                                                                            <!-- # -->
  </li>                                                                             <!-- # -->
</ul>
```

Now that we have 2 links in our navbar, we want to better style active links: we add `{% url 'home' as home %}` and `class "nav-link {% if request.path == home %}active{% endif %}"`.

### Override `form_valid`

Try to create an article in your app. When you hit “Publish”, you'll get an error:

> IntegrityError at /editor NOT NULL constraint failed: articles_article.author_id

This means that the issue is that the `author` value for the `Article` instance we're trying to create is `NULL`, which it shouldn't be. What we need to do in order to solve this issue is to somehow tell Django that the author is whoever's sending the request for creating the article: even though we haven't yet implemented authentication, we do have a user

The docs tell us that, when we want to track the user that created an object with a `CreateView`, we need to override the view's [`form_valid` method](https://docs.djangoproject.com/en/5.0/ref/class-based-views/mixins-editing/#django.views.generic.edit.ModelFormMixin.form_valid), which is called when some valid form data is POSTed.

In `articles/views.py`, we override the `form_valid` method of our `EditorCreateView`, following the example given in the docs:

``` { .python hl_lines="9-11" }
# ...
class EditorCreateView(CreateView):
    """create article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):                         # new
        self.object.author = self.request.user.profile  #
        return super().form_valid(form)                 #
```

Should work now, right? As expected, when we try to create an article again, we get an… error again?

> AttributeError at /editor ‘NoneType’ object has no attribute ‘author’

If we read our code again, we can pinpoint the issue to the fact that `self.object` does not exist. We need to create the object first.

Solving this requires understanding a bit more about forms. Behind the scenes, when we subclass a `CreateView` because we want to create new instances of a specific model, the forms that we're working with when creating new model instances are [`ModelForm` objects](https://docs.djangoproject.com/en/5.0/topics/forms/modelforms/), which map a model class's fields to HTML form `<input>` elements.

The `ModelForm` class has a [`save` method](https://docs.djangoproject.com/en/5.0/topics/forms/modelforms/#the-save-method) which “creates and saves a database object from the data bound to the form”. What we want to do is get that data, append a new field, then save the resulting object to the database. Well, we're in luck: /“If you call save() with commit=False, then it will return an object that hasn’t yet been saved to the database. \[…\] This is useful if you want to do custom processing on the object before saving it”/.

Let's try to take into account this new piece of knowledge:

``` { .python hl_lines="9-13" }
# ...
class EditorCreateView(CreateView):
    """create article"""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)           # new
        self.object.author = self.request.user.profile
        self.object.save()                              # new
        return super().form_valid(form)
```

The code above does the following:

- get the object from the data POSTed by the form
- set the logged in `profile` (which will always be `admin`, for now) as the `author`
- save the new object.

Try creating another article once you have added the code above to your view: a new article will be created and you will be redirected to its page.

Be aware however that you need to be logged in as admin for it to work, otherwise you'll get another error.

## Editing articles

We will now implement the editing feature.

### Subclass an `UpdateView`

You won't be surprised by now if we say that Django comes with a ready-made view for editing objects: the [`UpdateView` class-based view](https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/#updateview).

In `articles/views.py`, add the following:

``` { .python hl_lines="2 6-11" }
# ...
from django.views.generic import CreateView, DetailView, ListView, UpdateView

# ...

class EditorUpdateView(UpdateView):
    """View for editing articles."""

    model = Article
    fields = ["title", "description", "body"]
    template_name = "editor.html"
```

Nothing new here: we're going to be editing the `Article` model on the fields that we expose when creating new articles, and we'll use the same template for creating and editing articles.

### Add a `urlpattern`

In `articles/urls.py`, add:

``` { .python  }
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

Again, nothing new.

### Adapt `editor.html` template

Now we need to adapt our existing `templates/editor.html` template for cases where we're updating, rather than creating, articles.

In practice, this doesn't demand a lot of changes: we're still working on the same model, exposing the same fields, at the same URL.

The only thing that changes is that we want to have the form fields empty when the object doesn't exist yet (ie we're creating an article), and we want these fields prepopulated with the relevant values if the object exists already (ie we're updating).

Let's add the following to `templates/editor.html`:

``` { .html hl_lines="10 20 30" }
<!-- ... -->
<fieldset>
  {{ form.non_field_errors }}
  <fieldset class="form-group">
    <input
      class="form-control form-control-lg"
      type="text"
      placeholder="Article Title"
      name="{{ form.title.name }}"
      value="{{ form.title.value|default_if_none:'' }}"            <!-- new -->
    />
  </fieldset>
  {{ form.title.errors }}
  <fieldset class="form-group">
    <input
      class="form-control"
      type="text"
      placeholder="What's this article about?"
      name="{{ form.description.name }}"
      value="{{ form.description.value|default_if_none:'' }}"      <!-- new -->
    />
  </fieldset>
  {{ form.description.errors }}
  <fieldset class="form-group">
    <textarea
      class="form-control"
      rows="8"
      placeholder="Write your article (in markdown)"
      name="{{ form.body.name }}"
    >{{ form.body.value|default_if_none:'' }}</textarea>           <!-- new -->
  </fieldset>
  {{ form.body.errors }}
  <button class="btn btn-lg pull-xs-right btn-primary">
    Publish Article
  </button>
</fieldset>
<!-- ... -->
```

We are accessing the relevant values for our fields through `form.field_name.value`. However, when using `UpdateView`, we have access to the object being updated, so we have access to the relevant values through the `context_object_name` `article`, so you could write `article.title` instead of `form.title.value`, etc., if you prefer this alternative.

We're using a [`default_if_none` template filter](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#default-if-none) here: this filter provides a default value if the value of the preceding variable is `None`. If our article exists, it will have a title, description, and body, and the values of those fields will be presented in the form fields. If the article doesn't exist, we will just get the empty strings we defined as default.

### Add an *Edit* button to articles' pages

We want to expose our new editing functionality in our templates.

We will add a button for editing the article in `templates/article_meta.html`, based on the Svelte implementation's \[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\slug\\/\_ArticleMeta.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_ArticleMeta.svelte)\]\[\_ArticleMeta.svelte\]\]:

``` { .html hl_lines="10-19" }
<div class="article-meta">
  <div class="info">
    <span class="author">
      {{ article.author.user.username }}
    </span>
    <span class="date">
      {{ article.created_at|date:"D M d Y" }}
    </span>
  </div>
  <span>                                                            <!-- new -->
    <a                                                              <!-- # -->
      href="{% url 'editor_update' slug_uuid=article.slug_uuid %}"  <!-- # -->
      class="btn btn-outline-secondary btn-sm"                      <!-- # -->
    >                                                               <!-- # -->
      <span class="ion-edit">                                       <!-- # -->
        Edit Article                                                <!-- # -->
      </span>                                                       <!-- # -->
    </a>                                                            <!-- # -->
  </span>                                                           <!-- # -->
</div>
```

This is the first time that we pass parameters to a URL in a Django template.

We only just added a `urlpattern` to `articles/urls.py`, and we know that it takes a `slug_uuid` as a parameter, so we pass `article.slug_uuid` as an argument to our URL, as explained in the docs for the [`url` tag](https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#url).

### Adapt `get_object_or_404` method

Try navigating to an article: you should be able to view the *Edit* button. But try editing the thing and you'll just get an error:

> AttributeError at /editor/createview-50952832-f5b4-4f93-9edc-33aaa5f73565
>
> Generic detail view EditorUpdateView must be called with either an object pk or a slug in the URLconf.
>
> Request Method: GET Request URL: <http://127.0.0.1:8000/editor/createview-50952832-f5b4-4f93-9edc-33aaa5f73565>

Well well well, pretty sure we have seen an error just like this before… The `UpdateView` must be called with an object `pk` or a `slug`, but we have this `slug_uuid` field instead.

Since we've seen and solved this error when we were implementing `ArticleDetailView`, let's just go back and add the same code to `EditorUpdateView` in `articles/views.py`:

``` { .python hl_lines="7-9" }
# ...
class EditorUpdateView(UpdateView):
    """View for editing articles."""

    # ...

    def get_object(self):                                       # new
        slug_uuid = self.kwargs.get("slug_uuid")                #
        return get_object_or_404(Article, slug_uuid=slug_uuid)  #
```

We're just teaching our `EditorUpdateView` to retrieve the right `Article` instance based on a `slug_uuid` value.

Try editing an article now: you get a nice form with prepopulated fields, and can even save any changes!

## Deleting articles

Our users can now create and edit articles: the only missing functionality is article deletion. Let's get to it.

### Subclass a `DeleteView`

In `views.py`, we create a `ArticleDeleteView`:

``` { .python hl_lines="4" }
# ...
from django.views.generic import (
    # ...
    DeleteView,                                 # new
)

# ...
class EditorDeleteView(DeleteView):             # new
    """View for deleting articles."""           #
                                                #
    model = Article                             #
    template_name = "article_detail.html"       #
    success_url = reverse_lazy("home")          #
```

The `DeleteView` generic class-based view allows to delete an existing object.

The user will delete an article from the article's page, so that page will also be removed, and the user needs to be redirected to another URL after deletion: we will redirect the user to the `home` URL with [`reverse_lazy` URL resolver](https://docs.djangoproject.com/en/5.0/ref/urlresolvers/#reverse-lazy), which we need to use instead of `reverse` in class-based views.

In a second, we'll explain why we're using `templates/article_detail.html` as the template for this view, and why it's interesting.

### Add a `urlpattern`

First, let's create a `urlpattern` in `articles/urls.py`:

``` { .python hl_lines="4 9-13" }
# ...
from .views import (
    # ...
    EditorDeleteView,                           # new
)

urlpatterns = [
    # ...
    path(                                       # new
        "editor/<slug:slug_uuid>/delete",       #
        EditorDeleteView.as_view(),             #
        name="editor_delete",                   #
    ),                                          #
]
```

### Create a template

The common way to implement a `DeleteView` is to have a GET form on some page (for example, the article's detail page) that redirects to a confirmation page with a POST form that will delete the object. GET forms are used to construct a URL based on the data from the form: a good example are search forms, which take the data (a query, like “form”) and send it to a URL (like “<https://docs.djangoproject.com/search/?q=forms&release=1>”). POST forms, which we've covered before, are used to modify data server-side.

But that's not the workflow we want in the Realworld app: we should be able to delete an article straight from its detail page, which is why we specified `article_detail.html` template as our `template_name`. Implementing this will require some complicated code (relative to what we've written before), but we'll go through it slowly.

First, we'll create `templates/article_delete.html`: this will hold the form for deleting the article.

``` { .html  }
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

This is our POST form, the form that will delete the object identified by the parameter `slug_uuid` we're passing to the `editor_delete` URL. Since this is a POST form, it requires a `csrf_token` tag.

Now, we want to load this template in `article_meta.html` directly, alongside the *Edit* button. We'll do this with an `include` tag:

``` { .html hl_lines="11" }
<!-- ... -->
<span>
  <a
    href="{% url 'editor_update' slug_uuid=article.slug_uuid %}"
    class="btn btn-outline-secondary btn-sm"
  >
    <span class="ion-edit">
      Edit Article
    </span>
  </a>
  {% include 'article_delete.html' %}               <!-- new -->
</span>
<!-- ... -->
```

### Adapt `get_object_or_404` method

Before we try deleting an article, we remember that we need to teach our `ArticleDeleteView` to identify articles by their `slug_uuid`.

In `articles/views.py`:

``` { .python hl_lines="7-9" }
# ...
class EditorDeleteView(DeleteView):
    """View for deleting articles."""

    # ...

    def get_object(self):                                       # new
        slug_uuid = self.kwargs.get("slug_uuid")                #
        return get_object_or_404(Article, slug_uuid=slug_uuid)  #
```

Try deleting an article: you should get a nice confirmation message while still on the `article_detail.html` template, before the article is deleted.

