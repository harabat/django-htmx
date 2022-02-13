# Starting the project

## Introduction

Let's start this tutorial in earnest.

In this chapter, we'll set up everything we'll need to start coding: our
virtual environment, folders, user model, and database.

## Virtual environment

Before doing anything else, we need to create our virtual environment.

We're working with `conda`
([tutorial](https://docs.conda.io/en/latest/miniconda.html)), but you
can work with `virtualenv`
([tutorial](https://realpython.com/python-virtual-environments-a-primer/)).

``` { .shell }
conda create --name django
conda activate django
conda install django
```

Now, you have a virtual environment with `django` installed.

## Project layout

We'll be following a simplified version of the folder structure
described in the excellent [Two Scoops of
Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) by
Daniel and Audrey Feldroy (highly recommended if you want to know what
constitutes best practice in Django).

Our folder structure will look something like the following:

``` { .shell }
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

Let's create a folder for our project: we'll name it `django_tutorial`.

``` { .shell }
(django) ~$ mkdir conduit
```

We now create our project, `conduit`:

``` { .shell }
(django) ~$ cd conduit
(django) django_tutorial$ django-admin startproject conduit .
```

Our folder structure should look like this at this point:

```
django_tutorial
├── conduit
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
└── manage.py
```

We'll move all the files in the `conduit` folder into the
`django_tutorial/config` folder, as we explained above. The project
layout should now be:

```
.
├── conduit
│── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Because we're deviating from Django's generic project layout, we'll have
to update some lines in the settings. You might wonder why we have to
fiddle with the settings before even starting to code, but this small
effort has the benefit of making the structure of our project easier to
understand, and of separating the config from the code, which is a habit
to get into.

In `asgi.py` and `wsgi.py`:

``` { .python }
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# from os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conduit.settings")
```

In `settings.py`:

``` { .python }
ROOT_URLCONF = "config.urls"
# from ROOT_URLCONF = "conduit.urls"

WSGI_APPLICATION = "config.wsgi.application"
# from WSGI_APPLICATION = "conduit.wsgi.application"
```

Done, we have implemented a project layout that separates the config (in
the `config` folder) from the code (`conduit` folder) and told Django to
take this into account.

## App folder structure

Our app will have a lot of moving parts (articles, profiles, tags,
etc.). To keep the structure of our app clear, we'll host the logic for
each of these parts in separate folders.

We'll build Conduit step by step. The most basic function that the app
should have is the ability to post and read articles. Let's start with
that (you'll notice that this part is basically a repeat of Django Girls
tutorial's blog app).

``` { .shell }
(django) django_tutorial$ cd conduit
(django) conduit$ django-admin startapp articles
(django) conduit$ cd articles
```

Our folder structure now looks like this:

``` { .shell }
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
├── db.sqlite3
└── manage.py
```

We change the `name` line in the file `apps.py` in the `articles`
folder:

``` { .python hl_lines="6" }
from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conduit.articles'               # new
```

We also add the line `'conduit.articles',` to INSTALLED_APPS in
`settings.py`:

``` { .python hl_lines="9" }
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'conduit.articles', # add this line
]
```

## User model

[The Django docs warn
you](https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model):
“*If you're starting a new project, it's highly recommended to set up a
custom user model, even if the default User model is sufficient for you.
\[…\] Changing AUTH_USER_MODEL after you've created database tables is
significantly more difficult \[…\]. This change can't be done
automatically and requires manually fixing your schema, moving your data
from the old user table, and possibly manually reapplying some
migrations.*”. Scary stuff. Let's just follow the advice.

First, we need to create the app where we'll do everything that has to
do with users.

``` { .shell }
(django) conduit$ django-admin startapp users
```

We then change the `name` line in the file `apps.py` in the `articles/`
folder:

``` { .python hl_lines="6" }
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conduit.users'                  # new
```

Now, in `users/models.py`, add the following:

``` { .python }
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model"""

    pass
```

What we're doing here is take the `AbstractUser` model and save it as
is. This way, we can add any modifications we need later on.

In `users/models.py` we also need to create a `Profile` model: we'll
explain it in more detail later, but suffice it to say that the
`Profile` will deal with everything about our users that is not
authentication (logging in and out).

``` { .python }
class Profile(models.Model):
    """Profile model"""

    user = models.OneToOneField(User)
```

Now, create a superuser in the terminal, so as to be able to access
Django's admin app later on:

``` { .shell }
(django) django_tutorial$ python manage.py createsuperuser
```

And one last dark magic trick that you just need to do without asking
why (detailed explanations will be provided in a later section,
promise): in your terminal, in the `django_tutorial` folder, run the
following commands:

```
(django) django_tutorial$ python manage.py shell
```

And once you're in the IPython shell:

``` { .python }
Python 3.9.7 | packaged by conda-forge | (default, Sep 29 2021, 19:20:46)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.30.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from conduit.users.models import User, Profile

In [2]: user = User.objects.get(username='admin')

In [3]: user.profile = Profile.objects.create(user=user)
```

Finally, we need to tell Django that we're not using the default User
model. In `settings.py`, add your `users` app to `INSTALLED_APPS` and
point `AUTH_USER_MODEL` to it:

``` { .python hl_lines="4 7" }
# other settings
INSTALLED_APPS = [
    # other apps
    'conduit.users'
]

AUTH_USER_MODEL = 'users.User'
```

## Why no REST?

Because our entire frontend is integrated into Django (through HTML
templates and HTMX), and given the scope of tutorial, we can implement
the whole app without building a REST API. So we won't. This has a few
benefits:

-   we keep the structure of the app simple
-   we keep the mental load light: no need to understand how Django REST
    framework (the preferred way of implementing REST API in Django)
    works, no need to juggle with serializers, routers, renderers, etc.,
    no need to complicate the codebase
-   because we don't use REST API, we don't need to implement JWT
    authentication, which is a general pain: we can just rely on
    Django's built-in authentication solutions, which are robust and
    simple to implement.

## Create a database

Django uses a sqlite database by default: it's versatile, simple, and
sufficient for our needs, so we'll go with that, for now.

After any change to a model, we need to sync the database:

``` { .shell }
(django) django_tutorial$ python manage.py makemigrations
(django) django_tutorial$ python manage.py migrate
```

We'll be doing this many times throughout the tutorial: if your app
refuses to run at some point, the most likely error is that you forgot
to migrate, so make sure you keep on top of it.

## Bring the app online

Let's start the server.

``` { .shell }
(django) django_tutorial$ python manage.py runserver
```

Our app, Conduit, is online!

