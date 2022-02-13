# Users and Profiles

## Introduction

Time to work on our users and profiles.

[The Django docs
say](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#specifying-a-custom-user-model)
“*it may be more suitable to store app-specific user information in a
model that has a relation with your custom user model. That allows each
app to specify its own user data requirements without potentially
conflicting or breaking assumptions by other apps. It also means that
you would keep your user model as simple as possible, focused on
authentication, and following the minimum requirements Django expects
custom user models to meet.*”.

This is why we'll have the authentication logic in a `User` model and
the profile logic in a `Profile` model.

## User model

### Creating the User model

The `User` model will contain everything related to authentication.

We need an email, a username, and a password. Let's add the following to
the `User` model in `users/models.py`:

``` { .python }
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model"""

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        self.email
```

The `username` field is the unique human-readable identifier that we can
represent users with in our app. The `email` field holds the email users
will be logging in with. We specify this in `USERNAME_FIELD`. The
`password` field is already provided by `AbstractUser`.
`REQUIRED_FIELDS` is the list of field users will be prompted for at
sign up: because the `USERNAME_FIELD` and the `password` are already
required by Django, we only need to specify `username`. More information
about the fields can be found in the docs for [the default Django User
model](https://docs.djangoproject.com/en/4.0/ref/contrib/auth/).

### Creating the UserManager

We also need a `UserManager`, [as advised by the
docs](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model).
In `models.py`, we add the following, BEFORE we define our `User` model:

``` { .python }
# other imports
from django.contrib.auth.models import AbstractUser, UserManager

# other models
class CustomUserManager(UserManager):
    """custom UserManager with unique identifier is email instead of username"""

    def create_user(self, username, email, password=None):
        """Create and return a User with username, email, and password"""

        if email is None:
            raise ValueError("Email is required.")
        if username is None:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password=None):
        """Create and return a SuperUser with admin permissions."""

        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        return user
```

`create_user` and `create_superuser` are self-explanatory.

We now need to go back to the `User` model in `users/models.py` and
indicate to Django that the `UserManager` defined above will manage
objects of type `User`:

``` { .python hl_lines="11" }
# other
class User(AbstractUser):
    """User model"""

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()               # new

    def __str__(self):
        return self.email
```

Make sure to `makemigrations` and `migrate`, so that Django is aware of
your new model.

### Registering our new model

We need to register this new `User` model in `users/admins.py`, to have
access to it in our admin app.

``` { .python }
from django.contrib import admin
from .models import User

admin.site.register(User)
```

## Profile model

### Creating the Profile model

We are following the instructions in the Django docs about [extending a
User
model](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#extending-the-existing-user-model).
We need to store some information about our users in the database. Each
`User` object should be related to a single `Profile`, and vice-versa:
we'll use a
[`OneToOneField`](https://docs.djangoproject.com/en/4.0/ref/models/fields/#onetoonefield)
relationship.

Our `Profile` needs the following fields:

-   image
-   bio
-   articles
-   comments

We have already taken care of the two last fields in the `Article` and
`Comment` models through the `ForeignKey` relationships.

We will allow users to specify a URL to their avatar and to write a
short bio. This is optional, so we make sure to have `blank=True`. Let's
add the following to the `Profile` model in `users/models.py`:

``` { .python }
class Profile(models.Model):
    """Profile model"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.URLField(
        default="https://static.productionready.io/images/smiley-cyrus.jpg"
    )
    bio = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username
```

As always, whenever you change a model, you should `makemigrations` and
`migrate`.

### Automating the creation of profiles for each new user

Since we're defining the `Profile` outside of the `User` model, a
profile won't be created automatically whenever a user signs up.

Let's follow the docs linked above and code up a signal that creates a
`Profile` at user sign-up.

Create a `signals.py` file in the `users` folder and add the following:

``` { .python }
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile_for_user(sender, instance, **kwargs):
    instance.profile.save()
```

In order to activate this signal, we will modify `users/apps.py`:

``` { .python hl_lines="8-9" }
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conduit.users"

    def ready(self):                        # new
        import conduit.users.signals        # new
```

This signal runs whenever a `User` is saved. By checking for `created`,
we make sure to only initiate a `Profile` for the `User` instance if the
User has just been created, instead of whenever the instance is updated.

### Registering our new model

We need to register this new `Profile` model in `users/admins.py`, to
have access to it in our admin app, but we want to be able to view
`User` and `Profile` information for a given user in the same place.

``` { .python }
from django.contrib import admin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(admin.ModelAdmin):
    model = User
    inlines = [ProfileInline]


admin.site.register(User, UserAdmin)
```

You'll notice that this code is much shorter than [what the docs
say](https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#extending-the-existing-user-model):
we're trying to keep it simple, so we'll do without some of the quality
of life improvements that a more intricate code would allow.

