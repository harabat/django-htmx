# Slugs

## Introduction

We mentioned earlier that we didn't like having incrementing integers as primary keys for our articles, and we liked even less exposing these keys in the URL.

We want our article URLs to include slugs, which are easier to read than IDs.

We want the slugs to be unique, but some articles might have the same titles, which would generate the same slugs. One solution to this problem is to combine slugs with UUIDs.

Before continuing:

- slugs are the result of converting a string of text (generally a title) to a form that can be included in a URL: this generally consists in converting spaces to hyphens, removing special characters, and converting to lowercase
- a universally unique identifier (UUID) is a string of text expected to have an extremely low probability of duplication, without requiring a central authority to create them

## Define slug and UUID fields in the model

First, we need to modify our `Article` model to include `slug_uuid` and `uuid_field` fields in `articles/models.py`:

``` { .python hl_lines="2 7 8" }
# ...
import uuid                                                                     # new


class Article(models.Model):
    # ...
    slug_uuid = models.SlugField(max_length=100, editable=False)                # new
    uuid_field = models.UUIDField(default=uuid.uuid4, editable=False)           # new
```

We make both the `slug_uuid` and `uuid_field` uneditable because editing these fields is too error-prone to be facilitated (though admins will always be able to revert this temporarily if they need to).

After modifying the model, we need to sync the database, but this will return a warning.

``` shell
(django) django_tutorial$ python manage.py makemigrations
# It is impossible to add a non-nullable field 'slug_uuid' to article without specifying a default. This is because the database needs something to populate existing rows.
# Please select a fix:
#  1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
#  2) Quit and manually define a default value in models.py.
# Select an option:
```

Selecting `1` would have little value: a default is by definition non-unique, so we'll have to go and edit it later anyway. We select `2` to abort and add the `null=True` argument to the `slug_uuid` field: the field will become nullable (so the migration will be able to set 0 as default) and editable (so we'll be able to modify it manually through the Django admin):

``` { .python hl_lines="3-4" }
class Article(models.Model):
    # ...
    # slug_uuid = models.SlugField(max_length=100, editable=False)      # from this
    slug_uuid = models.SlugField(max_length=100, null=True)             # to this
    # ...
```

We run `makemigrations` and `migrate`:

``` shell
(django) django_tutorial$ python manage.py makemigrations
# Migrations for 'articles':
#   conduit/articles/migrations/0002_article_slug_uuid_article_uuid_field.py
#     - Add field slug_uuid to article
#     - Add field uuid_field to article
(django) django_tutorial$ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, articles, auth, contenttypes, sessions, users
# Running migrations:
#   Applying articles.0002_article_slug_uuid_article_uuid_field... OK
```

No error. We can go the Django admin, then set a unique slug for each `Article` manually: you can just slugify the titles you came up by hand, so “Making Slugs by Hand” would become “making-slugs-by-hand” for example.

<figure width="600">
<img src="../assets/admin - editing_slugs.png" />
<figcaption>Editing slugs</figcaption>
</figure>

Once we're done, we return to `articles/models.py` to remove the `null=True` argument and add the `editable=False` argument to `slug_uuid` again:

``` { .python hl_lines="3-4" }
class Article(models.Model):
    # ...
    # slug_uuid = models.SlugField(max_length=100, null=True)           # from this
    slug_uuid = models.SlugField(max_length=100, editable=False)        # to this
    # ...
```

When you make the migrations, you'll get a warning:

``` shell
(django) django_tutorial$ python manage.py makemigrations
# It is impossible to change a nullable field 'slug_uuid' on article to non-nullable without providing a default. This is because the database needs something to populate existing rows.
# Please select a fix:
#  1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
#  2) Ignore for now. Existing rows that contain NULL values will have to be handled manually, for example with a RunPython or RunSQL operation.
#  3) Quit and manually define a default value in models.py.
# Select an option: 2
# Migrations for 'articles':
#   conduit/articles/migrations/0003_alter_article_slug_uuid.py
#     - Alter field slug_uuid on article
```

You can safely select `2`, as we have already taken care of the `slug_uuid` fields through the Django admin app.

## Display slug and UUID fields in the Django admin

It'd be nice to be able to view our new fields in the Django admin, but non-editable fields are hidden by default.

In order to display these fields, we need to override how the Django admin represents the `Article` model.

In `articles/admin.py`, add the following:

``` { .python hl_lines="3-4 7-8" }
#...

class ArticleAdmin(admin.ModelAdmin):               # new
    readonly_fields = ("slug_uuid", "uuid_field")   #


# admin.site.register(Article)                      # from this
admin.site.register(Article, ArticleAdmin)          # to this
```

Here, we define subclass a [`ModelAdmin` class](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin) (which defines how a model is represented in the Django admin) and add the non-editable fields we want to see to the new class's [`readonly_fields` attribute](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields).

If you have a look at some of the existing articles, you'll be able to see their `slug_uuid` and `uuid_field` fields now.

## Generate unique `slug_uuid` fields with utility functions

We want to avoid manually entering the slugs for every article: the generation of a unique `slug_uuid` should be triggered automatically every time an `Article` instance is saved. Because our choice of slug is not the simplest, it doesn't come included with Django: we will need to create this functionality.

When we need to define new functions in order to add some new functionality to Django, the common pattern is to create a utility module (generally a `utils.py` file) and import the functions from there. This enables reuse, allows to keep code in models and views short, and facilitates testing. Depending on the scope of the utility functions, `utils.py` can be placed within the project, or simply at the level of the app.

In our case, we only need a function that will create unique slugs for articles, the scope of the utility module is the `articles` app, so we create the `utils.py` file in the `articles` folder:

``` { .python  }
from django.utils.text import slugify


def slug_uuid_generator(instance):
    """Generate a unique slug_uuid for Articles from the title and a UUID."""
    # if the instance already has a `slug_uuid`, don't change it
    # to avoid changing URLs
    if instance.slug_uuid:
        return instance.slug_uuid

    # get the instance's class (`Article`)
    ArticleClass = instance.__class__

    # get max length of `slug_uuid` as defined in the `Article` model
    max_length = ArticleClass._meta.get_field("slug_uuid").max_length

    uuid_field = str(instance.uuid_field)
    uuid_length = len(uuid_field)

    # slugify instance's title
    # trim slug to leave space for UUID
    slug_field = slugify(instance.title)[: max_length - uuid_length - 1]

    # create `slug_uuid` by concatenating slugified title and UUID
    slug_uuid = "{slug_field}-{uuid_field}".format(
        slug_field=slug_field,
        uuid_field=uuid_field,
    )

    return slug_uuid
```

This looks complicated, because it is, at our current level.

What we want to happen is the following: when a new article (ie a new instance of the `Article` model) is saved, we want a function to take that instance as an argument, extract its title and UUID, slugify the title, concatenate the slug with the UUID, and set the resulting string as that instance's `slug_uuid` field value. There's also a condition: if the article already has a `slug_uuid` (and is being saved after a simple update), then we don't want to change the `slug_uuid`, because that would change the URL and [cool URLs don't change](https://www.w3.org/Provider/Style/URI).

Walking through the function step by step, you can check that it is exactly what we're doing.

## Override `save` method instead of creating signals (alternative)

One way to call `slug_uuid_generator` at the moment of saving an article would be to [override](https://docs.djangoproject.com/en/5.0/topics/db/models/#overriding-model-methods) the `Article` model's [`save` method](https://docs.djangoproject.com/en/5.0/ref/models/instances/#saving-objects): this is a common method, but not [best practice](https://teddit.ggc-project.de/r/django/comments/p3pgr/overriding_save_vs_presave_signals_which_is/).

The next section is rather complicated, so if you prefer to keep things simple for now, you can just add the code below to your `articles/models.py` and skip straight to *Adapt URLs and views to `slug_uuid` fields*:

``` { .python hl_lines="2 8-10" }
# ...
from .utils import slug_uuid_generator              # new


class Article(models.Model):
    # ...

    def save(self, *args, **kwargs):                # new
        self.slug_uuid = slug_uuid_generator(self)  #
        super().save(*args, **kwargs)               #
```

We advise you to implement signals instead however, both in order to get some of that sweet Django learning, but also because this method will keep your code readable when your `save` method overrides start being 50 lines long.

## Generate `slug_uuid` fields automatically with signals

The function in the `utils.py` file should be called at the moment of saving a new `Article` instance: this step does not happen in the `utils.py` file, but in the file we will create next.

We create the `articles/signals.py` file and add the following method to it:

``` { .python  }
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Article
from .utils import slug_uuid_generator


@receiver(pre_save, sender=Article)
def generate_slug_uuid_before_article_save(sender, instance, *args, **kwargs):
    """Call slug_uuid_generator function when saving `Article` instance."""
    instance.slug_uuid = slug_uuid_generator(instance)
```

We use a signal to call our `slug_uuid_generator` every time an `Article` instance is created. [Signals](https://docs.djangoproject.com/en/5.0/topics/signals/) are a Django utility that allows applications (“receivers”) within Django to be notified (by “senders”) when certain actions happen.

In this case, the sender is the `Article` model. We want our `slug_uuid` to be generated just before an article is saved, so we want to use the [`pre_save` signal](https://docs.djangoproject.com/en/5.0/ref/signals/#pre-save), which is sent before a model's `save` method is called.

The receiver function `pre_save_receiver` generates a `slug_uuid` by calling `slug_uuid_generator`. We specify that `pre_save_receiver` is the receiver with the [receiver decorator](https://docs.djangoproject.com/en/5.0/topics/signals/#connecting-receiver-functions).

In order to activate this signal, we will modify `articles/apps.py`:

``` { .python hl_lines="8-9" }
from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conduit.articles"

    def ready(self):                        # new
        import conduit.articles.signals     # new
```

The [`ready` method](https://docs.djangoproject.com/en/5.0/ref/applications/#django.apps.AppConfig.ready) allows us to register the signals, and because we are using a `receiver` decorator, the signal handlers are [connected implicitly](https://docs.djangoproject.com/en/5.0/topics/signals/#connecting-receiver-functions) by just importing them.

We're ready to test our `slug_uuid` generation: let's try creating an Article through the Django admin app. Write some placeholder text in the title, description, and body, then select your superuser as the author, and save: you should be able to see the article in the Django admin and you can check that it has a nice `slug_uuid` value. Try changing the title of that article, save, and check that the `slug_uuid` has not changed.

## Adapt URLs and views to `slug_uuid` fields

Since we want to have `slug_uuid` parameters in our articles' URLs, we need to change `urlpatterns` in `articles/urls.py`:

``` { .python hl_lines="4-7" }
# ...
urlpatterns = [
    # ...
    # path("article/<int:pk>", ArticleDetailView.as_view(), name="article_detail"),     # from this
    path(                                                                               # to this
        "article/<slug:slug_uuid>", ArticleDetailView.as_view(), name="article_detail"  #
    ),                                                                                  #
]
```

Here, we tell Django's URL dispatcher to call the `ArticleDetailView` with the `slug_uuid` parameter, which is matched by the [`slug` path converter](https://docs.djangoproject.com/en/5.0/topics/http/urls/#path-converters) in the URL.

We're not finished just yet: if you navigate to your *Conduit* app at <http://127.0.0.1:8000/> and hover over the article previews, you'll see that the hyperlinks still point to URLs with a `pk` value. To remedy this, we need to update the `get_absolute_url` method in `articles/models.py`, so that our links in templates specify URLs with the article's `slug_uuid` value:

``` { .python hl_lines="6-7" }
# ...

class Article(models.Model):
    # ...
    def get_absolute_url(self):
        # return reverse("article_detail", kwargs={"pk": self.pk})              # from this
        return reverse("article_detail", kwargs={"slug_uuid": self.slug_uuid})  # to this
```

If you try to view a specific article now, you should get the following error:

> AttributeError at /article/onetoonefield
>
> Generic detail view ArticleDetailView must be called with either an object pk or a slug in the URLconf.
>
> Request Method: GET Request URL: <http://127.0.0.1:8000/article/onetoonefield>

This means that our `ArticleDetailView`, which is the interface that allows to identify the relevant model instance given a specific URL, is expecting either a `pk` or a `slug` parameter.

We have a few options:

- we can simply rename our `slug_uuid` fields to `slug` and be done with it
- we can teach our `ArticleDetailView` to identify `Article` instances based on the `slug_uuid` field

By now, you probably know that we're obviously going to choose the… second, more complicated option. Because we'll learn more that way.

In `articles/views.py`:

``` { .python hl_lines="2 6-8" }
#...
from django.shortcuts import get_object_or_404                  # new

class ArticleDetailView(DetailView):
    # ...
    def get_object(self):                                       # new
        slug_uuid = self.kwargs.get("slug_uuid")                #
        return get_object_or_404(Article, slug_uuid=slug_uuid)  #
```

Looks complicated, doesn't it? Wish we had chosen the easy way out. Anyway, let's try to understand.

When the URL dispatcher gets a request at a specific URL, it passes the data from the request (the URL itself, whether the user's logged in, whether the user's on a premium plan, etc.) to the view. Inside the view, we can access this data. The request data is included into the `self` argument that the [`get_object` method](https://docs.djangoproject.com/en/5.0/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_object) gets. From the request, we can extract the keyword arguments, or the kwargs. We're interested in the `slug_uuid` kwarg, specifically. Once we have the `slug_uuid` value, we can retrieve the desired `Article` model instance.

When going back to <http://localhost:8000/> (where your app is running), you will see that your new article has a `slug_uuid` consisting of its slugified title and a UUID:

<figure width="600">
<img src="../assets/article_detail - slug_uuid.png" />
<figcaption><code>slug_uuid</code> fields</figcaption>
</figure>

## `slug` and `uuid_field` instead of `slug_uuid` (alternative)

We have seen how to override the way instances of a model are retrieved by Django, but there is also a much simpler alternative to what we just did. Making slugs and UUIDs is a common requirement, so Django facilitates tasks around working with such fields.

The code below assumes that we are back to the very start of this chapter, just after finishing the *Viewing Articles* chapter.

In our `articles/models.py`, we create `slug` and `uuid_field` fields (we have to specify `null=True`, create `slug` values for the existing articles, then specify `editable=False`, like we did above):

``` { .python hl_lines="2 7 8" }
# ...
import uuid                                                                     # new


class Article(models.Model):
    # ...
    slug = models.SlugField(max_length=68, editable=False)                      # new
    uuid_field = models.UUIDField(default=uuid.uuid4, editable=False)           # new
```

Still in `articles/models.py`, we override the `save` method to generate slugs at save:

``` { .python hl_lines="2 8-10" }
# ...
from django.utils.text import slugify                                           # new


class Article(models.Model):
    # ...

    def save(self, *args, **kwargs):                                            # new
        self.slug = slugify(self.title)                                         # new
        super().save(*args, **kwargs)                                           # new
```

In `articles/urls.py`, we add our new URL:

``` { .python hl_lines="4-7" }
# ...
urlpatterns = [
    # path("article/<int:pk>", ArticleDetailView.as_view(), name="article_detail"),                 # from this
    path(                                                                                           # to this
        "article/<slug:slug>-<uuid:uuid>",                                                          #
        ArticleDetailView.as_view(),                                                                #
        name="article_detail",                                                                      #
    ),                                                                                              #
]
```

In `articles/models.py`, we adapt `get_absolute_url`:

``` { .python hl_lines="6-7" }
# ...

class Article(models.Model):
    # ...
    def get_absolute_url(self):
        # return reverse("article_detail", kwargs={"pk": self.pk})                  # from this
        return reverse(                                                             # to this
            "article_detail", kwargs={"slug": self.slug, "uuid": self.uuid_field}   #
        )                                                                           #
```

And finally we adapt the view in `articles/views.py`:

``` { .python hl_lines="2 6-8" }
#...
from django.shortcuts import get_object_or_404                                  # new

class ArticleDetailView(DetailView):
    # ...
    def get_object(self):                                                       # new
        slug = self.kwargs.get("slug")                                          #
        uuid_field = self.kwargs.get("uuid")                                    #
        return get_object_or_404(Article, slug=slug, uuid_field=uuid_field)     #
```

