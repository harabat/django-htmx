# Starting the project

## Introduction

Let's start this tutorial in earnest.

In this chapter:

- we'll set up everything we'll need to start coding (our virtual environment and our project directories)
- we'll learn how to structure a Django project, how to create applications, how to change settings
- we'll write several models, create a database, use the famed Django admin, and finally get our app running locally.

## Virtual environment

Before doing anything else, we need to create our virtual environment.

We're working with `conda` ([tutorial](https://docs.conda.io/en/latest/miniconda.html)), but you can use your favourite virtual lib, like `virtualenv` ([tutorial](https://realpython.com/python-virtual-environments-a-primer/)).

``` shell
~$ conda create --name django
(django) ~$ conda activate django
(django) ~$ conda install django faker
```

Now, you have a virtual environment with `django` and `faker` installed.

## Project layout and folder structure

We'll be following a simplified version of the folder structure described in the [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) by Daniel and Audrey Feldroy.

We want our folder structure to look something like the following:

``` shell
folder_name
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── project_name/
│   ├── app_1/
│   ├── app_2/
│   ├── static/
│   └── templates/
├── .gitignore
├── manage.py
└── db.sqlite3
```

Before we get there, however, we need to go through the Django defaults.

Let's create a folder for our project: we'll name it `django_tutorial`. After that, we'll create our project, `conduit`, inside `django_tutorial`:

``` shell
(django) ~$ mkdir django_tutorial
(django) ~$ cd django_tutorial
(django) django_tutorial$ django-admin startproject conduit .
```

!!! Advice

    We strongly recommend you use git when going through this tutorial.

Our folder structure should look like this at this point:

```
django_tutorial
├── conduit
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

We'll move all the files in the `conduit` folder into the `django_tutorial/config` folder, as we explained above. The project layout should now be:

```
django_tutorial
├── conduit
│── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Because we're deviating from Django's generic project layout, we'll have to update some lines in the settings. You might wonder why we have to fiddle with the settings before even starting to code, but this small effort has the benefit of making the structure of our project easier to understand, and of separating the config from the code, which is a good habit to get into.

In `config/asgi.py`, `config/wsgi.py`, and `./manage.py`, we update the location of our `settings.py` file:

``` { .python hl_lines="3-4" }
# ...

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conduit.settings")       # from this
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")          # to this
```

We do the same in `config/settings.py`:

``` { .python hl_lines="3-4 6-7" }
# ...

# ROOT_URLCONF = "conduit.urls"         # from this
ROOT_URLCONF = "config.urls"            # to this

# WSGI_APPLICATION = "conduit.wsgi.application"     # from this
WSGI_APPLICATION = "config.wsgi.application"        # to this
```

Done! We have implemented a project layout that separates the config (in the `config` folder) from the code (in the `conduit` folder) and told Django to take this into account.

Our app will have a lot of moving parts (articles, profiles, tags, etc.). To keep the structure of our app clear, we'll host the logic for each of these parts in separate folders.

We'll build *Conduit* step by step.

## `articles` application

The most basic function that the *Conduit* app should have is the ability to post and read articles. Let's start with that (you'll notice that this part is basically a repeat of [DjangoGirls tutorial](https://github.com/DjangoGirls/tutorial)'s blog app).

We'll create an `articles` [application](https://docs.djangoproject.com/en/5.0/ref/applications/#projects-and-applications) (a package that provides a specific set of features) that will hold all the logic that is related to dealing with articles.

``` shell
(django) django_tutorial$ cd conduit
(django) conduit$ django-admin startapp articles
(django) conduit$ cd articles
```

Our folder structure now looks like this:

``` shell
django_tutorial
├── conduit
│   ├── articles
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
├── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Because of our folder structure, we will need to make a small adjustment in the file `articles/apps.py`:

``` { .python hl_lines="6-7" }
from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # name = "articles"             # from this
    name = "conduit.articles"       # to this
```

We also add the `articles` application to the [`INSTALLED_APPS` setting](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-INSTALLED_APPS) in `config/settings.py`, in order to let Django know about our new app `articles`:

``` { .python hl_lines="8" }
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "conduit.articles",             # new
]
```

## `users` app and `User` model

[The Django docs warn you](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#substituting-a-custom-user-model): “*If you're starting a new project, it's highly recommended to set up a custom user model, even if the default User model is sufficient for you. \[…\] Changing AUTH_USER_MODEL after you've created database tables is significantly more difficult \[…\]. This change can't be done automatically and requires manually fixing your schema, moving your data from the old user table, and possibly manually reapplying some migrations.*”.

Scary stuff. Let's just follow the advice.

First, we need to create the app where we'll put all the logic that has to do with users.

``` shell
(django) conduit$ django-admin startapp users
```

We remember to take into account our folder structure in `users/apps.py`:

``` { .python hl_lines="6-7" }
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # name = "users"            # from this
    name = "conduit.users"      # to this
```

And we add the new `users` application to our `INSTALLED_APPS` in `config/settings.py`:

``` { .python hl_lines="4" }
# ...
INSTALLED_APPS = [
    # ...
    "conduit.users",            # new
]
```

Now, in `users/models.py`, add the following:

``` { .python hl_lines="1 5-8" }
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model."""

    pass
```

What we're doing here is exactly [what the Django docs advise us to do](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project): we take the `AbstractUser` model and save it as is, which will provide us with a custom user model. This way, we can add any modifications that we need later on.

Finally, we need to tell Django that we're not using the default `User` model. In `config/settings.py`, point [`AUTH_USER_MODEL`](https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-AUTH_USER_MODEL) to it:

``` { .python hl_lines="2" }
# ...
AUTH_USER_MODEL = "users.User"      # new
```

Great, our `user` application and our custom `User` model are ready.

## Create a database

Django uses a SQLite database by default: it's versatile, simple, and sufficient for our needs. Django also supports other databases, notably PostgreSQL, which is what we would want to use if our app was expected to grow fast, but for now we will stay with SQLite.

!!! Info

    We would arguably learn more by setting up a PosgreSQL database: SQLite is a “set it and forget it”, “just works” type of thing. Since learning more is the point of this tutorial, we might shift to PostgreSQL at some point.

After any change to a model, we need to sync the database so that the changes [can be propagated into the database schema](https://docs.djangoproject.com/en/5.0/topics/migrations/). If you don't yet know what that means, no worries: we'll have a much closer look at what exactly is in our database, and what happens when we run migrations.

Specifically in this case, we want Django to create an `Article` table that will hold our articles.

Since we changed the `Articles` model, we will run the following commands:

``` shell
(django) django_tutorial$ python manage.py makemigrations
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, users
(django) django_tutorial$ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, users
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying contenttypes.0002_remove_content_type_name... OK
#   Applying auth.0001_initial... OK
#   Applying auth.0002_alter_permission_name_max_length... OK
#   Applying auth.0003_alter_user_email_max_length... OK
#   Applying auth.0004_alter_user_username_opts... OK
#   Applying auth.0005_alter_user_last_login_null... OK
#   Applying auth.0006_require_contenttypes_0002... OK
#   Applying auth.0007_alter_validators_add_error_messages... OK
#   Applying auth.0008_alter_user_username_max_length... OK
#   Applying auth.0009_alter_user_last_name_max_length... OK
#   Applying auth.0010_alter_group_name_max_length... OK
#   Applying auth.0011_update_proxy_permissions... OK
#   Applying auth.0012_alter_user_first_name_max_length... OK
#   Applying users.0001_initial... OK
#   Applying admin.0001_initial... OK
#   Applying admin.0002_logentry_remove_auto_add... OK
#   Applying admin.0003_logentry_add_action_flag_choices... OK
#   Applying sessions.0001_initial... OK
```

We'll be doing this many times throughout the tutorial: if your app refuses to run at some point, the most likely error (from experience) is that you forgot to migrate, so make sure you keep on top of it.

## Create a superuser

One of Django's greatest advantages is its admin app: it is considered so helpful that you probably will see it mentioned in most discussions about Django.

To be able to access the admin app (which we will do in a later section), we need a [superuser](https://docs.djangoproject.com/en/5.0/topics/auth/default/#creating-superusers). Run the following and fill the values (you don't need a real email or a strong password here):

``` shell
(django) django_tutorial$ python manage.py createsuperuser
# Username (leave blank to use $CURRENTUSER): admin
# Email address: admin@example.com
# Password:
# Password (again):
# Superuser created successfully.
```

## `Profile` model

In `users/models.py` we also need to create a `Profile` model: we'll explain it in more detail later, but suffice it to say that the `Profile` will deal with everything about our users that is not authentication (ie logging in and out).

``` { .python hl_lines="3-9" }
# ...

class Profile(models.Model):
    """Profile model associated to each User object."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
```

We'll go through the code step by step:

- The docs for the [`OneToOneField` model field](https://docs.djangoproject.com/en/5.0/ref/models/fields/#onetoonefield) read: “*A one-to-one relationship. Conceptually, this is similar to a ForeignKey with unique=True, but the “reverse” side of the relation will directly return a single object. This is most useful as the primary key of a model which “extends” another model in some way*”. This is exactly we need, because each `User` has one associated `Profile`, and each `Profile` corresponds to a single `User`.
- [`on_delete` is a required argument](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ForeignKey.on_delete) for `OneToOneField` and specifies what happens when the model instance is deleted.
- the [`__str__` method](https://docs.djangoproject.com/en/5.0/ref/models/instances/#str) tells Django what the string representation of the model should be: this is how specific model instances will be represented in the Django admin app, in the shell, in the error messages, in the templates, etc. Here, we specify that we want our profiles to be referenced by the associated user's username.

Now that we have a `Profile` model, we want to create one for our existing user (the `admin` superuser). Later on, we will automate the creation of a profile for every new user, but this is not implemented yet, so we need to do it manually. Well, thankfully Django allows us to interact with it [through a Python shell](https://docs.djangoproject.com/en/5.0/ref/django-admin/#shell).

``` shell
(django) django_tutorial$ python manage.py shell
```

And now that we're in the IPython shell, we will interact with the Django ORM: we will get our `admin` user from the `User` objects and then create a `Profile` instance.

``` { .python  }
In [1]: from django.contrib.auth import get_user_model

In [2]: from conduit.users.models import Profile

In [3]: user = get_user_model().objects.get(username='admin')

In [4]: user.profile = Profile.objects.create(user=user)
```

You might wonder why we're importing `get_user_model` instead of the `User` model directly: this is [best practice](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/#django.contrib.auth.get_user_model) and ensures we're working with the currently active user model.

However, if you've been following up to now… you should have gotten an error above. Namely, you should have gotten:

> OperationalError: no such table: users_profile

90% of programming is writing code, and the other 90% of programming is debugging, as the saying goes, so we might as well learn to deal with Django's errors while learning Django. The error above says that our database has no table `users_profile`: why might that be? Because we didn't sync our database after modifying our models!

Open a new terminal session and run migrations:

``` shell
(django) django_tutorial$ python manage.py makemigrations
# Migrations for 'users':
#   conduit/users/migrations/0002_profile.py
#     - Create model Profile
(django) django_tutorial$ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, users
# Running migrations:
#   Applying users.0002_profile... OK
```

Now return to the previous session and rerun the shell command: there should be no error this time.

## Start the server

We have everything we need to actually run our app. Let's [start the server](https://docs.djangoproject.com/en/5.0/ref/django-admin/#runserver)!

``` shell
(django) django_tutorial$ python manage.py runserver
```

You should see this:

<figure width="600">
<img src="../assets/server - run.png" />
<figcaption>python manage.py runserver</figcaption>
</figure>

Our app, *Conduit*, is online!

## `Article` model

We'll start by making a model for our articles.

When creating a model, we need to think of what fields the model will need. Let's take 2 seconds to think. Any article needs:

- a title
- a body (the text)
- a description
- an author
- a creation date.

Let's implement that in `articles/models.py`.

``` { .python  }
from django.db import models


class Article(models.Model):
    """Article model."""

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
```

Let's explain everything step by step:

- the article's `title` will be used as `db_index`: when we do queries on articles in our database, we'll often be looking at the `title`, so having this field as index will speed the queries
- `description` and `body` are self-explanatory
- `author` is a bit more complicated:
  - the [`ForeignKey` model field](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ForeignKey) allows us to have a many-to-one relationship: multiple articles for every profile
  - we have seen `on_delete`, but not [`related_name`](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ForeignKey.related_name): `related_name="articles"` allows us to access a user's (or rather profile's) articles through an `articles` attribute (for example, `User.articles.all()` to get the `admin` user's articles)
- `auto_now_add` simply records the time of creation for `created_at`
- the `__str__` method says that the string representation of an article will be its title

Let's sync the database again:

``` shell
(django) django_tutorial$ python manage.py makemigrations
# Migrations for 'articles':
#   conduit/articles/migrations/0001_initial.py
#     - Create model Article
(django) django_tutorial$ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, articles, auth, contenttypes, sessions, users
# Running migrations:
#   Applying articles.0001_initial... OK
```

## Using the Django admin

In order to have something to work with for the rest of the tutorial, we need to create some posts. Because we can't yet do it through *Conduit*, we will do so through Django admin.

In order for the Django admin to [have access to the `Article` model](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#modeladmin-objects), we need to register it in `articles/admin.py`:

``` { .python hl_lines="2 4" }
from django.contrib import admin
from .models import Article             # new

admin.site.register(Article)            # new
```

That's it, the `Article` model is now editable through the Django admin. The server should still be running (otherwise restart it). We will go to the Django admin app (<http://127.0.0.1:8000/admin/>) and log in as the superuser (`admin` in my case) that we created earlier.

Once we're logged in, we will create three articles in Django admin:

1.  click “:heavy-plus-sign: Add” in the `Articles` section
2.  specify a title, a description, a body, and the author (you) for the article
3.  click “Save and add another”

