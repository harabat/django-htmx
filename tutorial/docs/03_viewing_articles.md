# Viewing Articles

## Introduction

In this chapter, we'll let our users navigate to and read individual
articles.

## Article view

First, we need to implement the article view.

First, we create a view in `views.py`:

``` { .python hl_lines="1 5-9" }
from django.views.generic import DetailView, ListView       # new

# ...

class ArticleDetailView(DetailView):
    """Detail view for individual articles."""

    model = Article
    template_name = "article_detail.html"
```

We're continuing to work with class-based views here. The [`DetailView`
generic display
view](https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/#detailview)
allows to view a single instance of an object. We specify the model this
view will be associated to and the template name.

## Article URLs and primary keys

We now match a URL to the `ArticleDetailView` in `articles/urls.py`:

``` { .python hl_lines="1 5" }
from .views import ArticleDetailView, Home                                              # new

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("article/<int:pk>", ArticleDetailView.as_view(), name="article_detail"),       # new
]
```

This is the first time we're actually specifying a URL with arguments.

Django's [URL dispatcher
docs](https://docs.djangoproject.com/en/4.0/topics/http/urls/) have a
lot of information on the ins and outs, but for now we only need to know
that the current URL comprises an `articles/` prefix and the article's
key.

The `<int:pk>` parameter here matches any integer, and transfers the
captured value to `ArticleDetailView`, which tries to identify the
article based on its primary key (`pk`): primary keys are a way to
uniquely specify a record in a database. Since we didn't specify how to
generate primary keys for the `Article` objects in our database, this
will default to an incrementing integer (the first article will have a
`pk` of 1, the next will have a `pk` of 2, etc.).

To have an idea, and to practice your shell skills, launch the
interactive shell (by running `python manage.py shell`) and run the
following commands:

``` { .python }
Python 3.9.13 | packaged by conda-forge | (main, May 27 2022, 16:56:21)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.33.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from conduit.articles.models import Article

In [2]: Article.objects.all()
Out[2]: <QuerySet [<Article: ForeignKey>, <Article: ManyToManyField>, <Article: OneToOneField>]>

In [3]: Article.objects.first().pk
Out[3]: 1

In [4]: Article.objects.last().pk
Out[4]: 3
```

The concept of incrementing integers as the primary key has several
flaws, the main one being that anyone can infer how many articles you
publish, how many users you have, etc. just by looking at the URL. And
the URLs are plain unclear. We'll change the primary keys later on.

## get_absolute_url method

In order for `ArticleDetailView` to be able to identify an `Article`
object from its `pk`, we need to modify the `Article` model in
`articles/models.py` (don't forget to sync the database immediately
after):

``` { .python hl_lines="2 10-11" }
from django.db import models
from django.shortcuts import reverse                                # new


class Article(models.Model):
    """Article model."""

    # ...

    def get_absolute_url(self):                                     # new
        return reverse("article_detail", kwargs={"pk": self.pk})    #
```

The [`get_absolute_url`
method](https://docs.djangoproject.com/en/4.0/ref/models/instances/#get-absolute-url)
tells Django how to generate the URL for the instance. The [`reverse`
function](https://docs.djangoproject.com/en/4.0/ref/urlresolvers/#reverse)
takes a `urlpattern` (`article_detail` here), required kwargs (the
instance's `pk` here), and returns a URL, which avoids having to
hardcode it.

You can have a look at how it works in the shell:

``` { .python }
In [1]: from conduit.articles.models import Article

In [2]: from django.urls import reverse

In [3]: article = Article.objects.first()

In [4]: reverse('article_detail', kwargs={'pk': article.pk})
Out[4]: '/article/1'
```

## Article templates

Like in the previous chapter, after making a view and setting the URL,
we will now work on templates.

### article_detail.html

We create the `templates/article_detail.html` template with the
following code:

``` { .html }
{% extends "base.html" %}
{% block title %}
  <title>{{ article.title }} - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
  <div class="article-page">
    <div class="banner">
      <div class="container">
        <h1>{{ article.title }}</h1>
        {% include "article_meta.html" %}
      </div>
    </div>
    <div class="container page">
      <div class="row article-content">
        <div class="col-xs-12">
          <div>
            {{ article.body|linebreaks }}
          </div>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```

Not much to explain:

-   we're overriding the `title` block of `base.html` with a
    `{% block title %}` to display the title of the article (and our
    app's name): this is an illustration of template inheritance, which
    we mentioned earlier
-   in the `content` block of `base.html`:
    -   we refer to our object as `article`: the [default
        `context_object_name`
        variable](https://docs.djangoproject.com/en/4.0/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_context_object_name)
        (the way you refer to the object that the view is manipulating)
        in for `DetailView` (among others) is the model's name
        (`Article`) in lowercase
    -   we're showing the article's title
    -   we're including a `templates/article_meta.html` template simply
        because we're following Svelte implementation's
        \[\[<https://github.com/sveltejs/realworld/blob/master/src/routes/article/%5Bslug%5D/index.svelte>\]\[article/\[slug\]/index.svelte\]\]
        and we might as well keep to their structure if you ever need to
        quickly compare things
    -   the [`linebreaks` template
        filter](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#linebreaks)
        ensures that the line breaks in our articles are properly
        translated to HTML and rendered.

### article_meta.html

We create `templates/article_meta.html`, based on the Svelte
implementation's
\[\[[https://github.com/sveltejs/realworld/blob/master/src/routes/article/\\\[slug\\\]/\_ArticleMeta.svelte](https://github.com/sveltejs/realworld/blob/master/src/routes/article/\%5Bslug\%5D/_ArticleMeta.svelte)\]\[\_ArticleMeta.svelte\]\]:

``` { .html }
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
```

We display the author's username and the article's creation date
(properly formatted with the [`date` template
filter](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#date)).

### article_preview.html

Finally, we modify `template/article_preview.html` so that article
previews redirect to the full articles:

``` { .html hl_lines="3" }
<!-- ... -->
<!-- <a href="" rel="prefetch" class="preview-link"> -->                        <!-- from this -->
<a href="{{ article.get_absolute_url }}" rel="prefetch" class="preview-link">   <!-- to this -->
   <h1>{{ article.title }}</h1>
   <p>{{ article.description }}</p>
   <span>Read more...</span>
</a>
<!-- ... -->
```

We implemented the `get_absolute_url` method in our `Article` model
earlier, which allows to specify the URLs to instances by calling the
instance's `get_absolute_url` method.

### Results

Seems like we're ready, doesn't it? If you try to navigate to an article
in your *Conduit* app, you should be able to view your articles.

Let's see what it looks like:

<figure>
<img src="./assets/article_detail.png" width="600"
alt="Individual article in our app" />
<figcaption aria-hidden="true">Individual article in our
app</figcaption>
</figure>

<figure>
<img src="./assets/article_detail - realworld.png" width="600"
alt="Individual article in RealWorld app" />
<figcaption aria-hidden="true">Individual article in RealWorld
app</figcaption>
</figure>

Getting pretty close!

