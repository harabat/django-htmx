# Follows

## Creating a few new users and articles

To make the following sections more interesting, let's create a new
users and posts. Run Django shell with
`(django) django_tutorial$ python manage.py shell` and then paste the
following into your shell (no need to clean it):

``` { .python }
In [1]: from conduit.users.models import Profile, User
In [2]: from conduit.articles.models import Article
In [3]: from faker import Faker
In [4]: fake = Faker()
In [5]: fake.seed_instance(42)
In [6]: for i in range(2):
   ...:     user = User.objects.create_user(username=fake.user_name(), email=fake.email(), password=fake.password())
   ...:     profile = user.profile
   ...:     profile.image = fake.image_url(600, 600)
   ...:     profile.bio = fake.text()
   ...:     user.save()
   ...:     for j in range(2):
   ...:         Article.objects.create(
   ...:             author=Profile.objects.last(),
   ...:             title=fake.sentence(),
   ...:             description=fake.paragraph(),
   ...:             body=fake.text()
   ...:         )
   ...:
In [7]: User.objects.get(username='admin').profile.follow(Profile.objects.last())
```

This will create 2 users with full profiles and a couple articles each.

## Model

We'll now let our users follow other users, ie subscribe to other users'
articles. This should be a relationship between `Profile` objects, where
one `Profile` object can follow, and be followed by, many other
`Profile` objects: we'll use a
[`ManyToManyField`](https://docs.djangoproject.com/en/4.0/ref/models/fields/#django.db.models.ManyToManyField)
relationship.

We need a new field in our `Profile` model in `users/models.py`:

``` { .python }
# other models
class Profile(models.Model):
    # ...
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )
    # ...
```

The args we pass to the `ManyToManyField` signify that the relationship
works between `Profile` objects, that we can get the `Profile` objects
followed by a given `Profile` with the `follows` attribute, that we can
know who's following a given `Profile` with the `followed_by` attribute,
and that follows are a one-way relationship (it's not because User A
follows User B that User B necessarily follows User A).

We also need to define a few methods that will be helpful later on. In
`users/models.py`:

``` { .python }
class Profile(models.Model):
    # ...
    def follow(self, profile):
        """Follow `profile`"""
        self.follows.add(profile)

    def unfollow(self, profile):
        """Unfollow `profile`"""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Return True if `profile` is in self.follows, False otherwise"""
        return self.follows.filter(pk=profile.pk).exists()
```

Let's `makemigrations` and `migrate`, since we have modified the model.

``` { .shell }
(django) django_tutorial$ python manage.py makemigrations
# ...
(django) django_tutorial$ python manage.py migrate
# ...
```

## ProfileDetailView

We need to let users to follow or unfollow other users in our templates.
This involves some work around checking whether the user is already in
our `follows` or not. Because the Django Template Language
(intentionally) makes it difficult to write non-trivial queries within
templates, we'll have to do some groundwork in our views, with the help
of the model methods we just created.

In `users/views.py`, we add `is_following` to the context of
`ProfileDetailView` to enable our template to know whether the
authenticated user follows a given profile:

``` { .python hl_lines="7" }
class ProfileDetailView(DetailView):
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["my_articles"] = self.object.articles.order_by('-created_at')
            context["is_following"] = self.object.is_following(self.object)     # new
        return context
```

Still in `users/views.py`, we add a RedirectView whose only purpose is
to follow or unfollow a profile, depending on whether or not the profile
is followed already.

In `users/urls.py`:

``` { .python }
# other imports
from .views import (
    # ...
    ProfileFollowView,
)


urlpatterns = [
    # other paths
    path(
        "profile/@<str:username>/follow",
        ProfileFollowView.as_view(),
        name="profile_follow",
    ),
]
```

Let's implement the `follow` functionality in
`templates/profile_detail.html` now:

``` { .html hl_lines="14-15" }
<div class="col-xs-12 col-md-10 offset-md-1">
  <img src="{{ profile.image }}" class="user-img" alt="{{ profile.user.username }}" />
  <h4>{{ profile.user.username }}</h4>
  <p>{{ profile.bio|default:"This user doesn't have a bio for now" }}</p>
  {% if user.username == profile.user.username %}
    <a
      href="{% url 'settings' %}"
      class="btn btn-sm btn-outline-secondary action-btn"
    >
      <span class="ion-gear-a">
        Edit Profile Settings
      </span>
    </a>
  {% else %}                                <!-- new -->
    {% include 'profile_follow.html' %}     <!-- new -->
  {% endif %}
</div>
```

Create `templates/profile_follow.html`:

``` { .html }
<form
  method="post"
  action="{% url 'profile_follow' username=profile.user.username %}"
>
  {% csrf_token %}
  <button class="btn btn-sm action-btn
                 {% if is_following %}
                 btn-secondary
                 {% else %}
                 btn-outline-secondary
                 {% endif %}"
  >
    <span class="ion-plus-round">
      {% if is_following %}Unfollow{% else %}Follow{% endif %} {{ profile.user.username }}
    </span>
  </button>
</form>
```

What we're doing in this template is the following:

-   if the user's viewing their own profile, show a link to the
    `settings` URL.
-   if the user's viewing another profile (or is not logged in),
    redirect them to the `profile_follow` URL, which toggles a `Profile`
    object's `follow` and `unfollow` methods
-   adapt the text and UI based on whether the user's following the
    viewed profile via a bunch of `{% if ...%}` template tags.

## ArticleDetailView

We also expose the follow/unfollow feature on article pages.

In `articles/views.py`:

``` { .python }
class ArticleDetailView(DetailView):
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentCreateView().get_form_class()
        if self.request.user.is_authenticated:
            context["is_following"] =   self.request.user.profile.is_following(
                self.object.author
            )
        return context
```

In `templates/article_detail.html`:

``` { .html hl_lines="13-16" }
{% if user == article.author.user %}
  <span>
    <a
      href="{% url 'editor_update' slug=article.slug %}"
      class="btn btn-outline-secondary btn-sm"
    >
      <span class="ion-edit">
        Edit Article
      </span>
    </a>
    {% include 'article_delete.html' %}
  </span>
{% else %}                                                          <!-- new -->
  <span>                                                            <!-- new -->
    {% include 'profile_follow.html' with profile=article.author %} <!-- new -->
  </span>                                                           <!-- new -->
{% endif %}
```

In `templates/profile_follow.html`, we add `style="display:inline"`:

``` { .html }
<form
    method="post"
    action="{% url 'profile_follow' username=profile.user.username %}"
    style="display:inline"
>
<!-- ... -->
```

An interesting aside: for the longest time, I tried to follow or
unfollow a profile based on whether the template form had
`method="post"` or `method="delete"` (because `RedirectView` has both
`post` and `delete` methods), only to discover that [HTML forms only
support `GET` and
`POST`](https://stackoverflow.com/questions/165779/are-the-put-delete-head-etc-methods-available-in-most-web-browsers)
and that [workarounds are not very
pretty](https://stackoverflow.com/questions/27203547/django-csrf-token-invalid-after-modifying-request).
Live and learn.

## Redirect URL

If you play around with the `Follow` feature, you will notice that it
redirects us to the profile page of the user we want to (un)follow. This
is due to the fact that the `Follow` button is exposed both in
`profile_detail.html` and in `home.html` (through
`article_preview.html`), so for the sake of simplicity we chose a single
redirect URL in our `ProfileFollowView`.

However, it would be better if we could stay on whatever page we are
when we follow a user. This involves implementing the `next` kwarg.

In `templates/profile_follow.html`:

``` { .html hl_lines="6" }
<form
    method="post"
    action="{% url 'profile_follow' username=profile.user.username %}"
    style="display:inline"
>
    <input type="hidden" name="next" value="{{ request.path }}">    <!-- new -->
    {% csrf_token %}
    <button class="btn btn-sm action-btn
                   {% if is_following %}
                   btn-secondary
                   {% else %}
                   btn-outline-secondary
                   {% endif %}"
    >
        <span class="ion-plus-round">
            {% if is_following %}Unfollow{% else %}Follow{% endif %} {{ profile.user.username }}
        </span>
    </button>
</form>
```

The `next` parameter above just holds the URL that the `profile_follow`
URL pattern was called from.

In `users/views.py`:

``` { .python }
class ProfileFollowView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get("next", None)
        if url:
            return url
        else:
            return super().get_redirect_url(*args, **kwargs)

    # ...
```

We override the `get_redirect_url` method of `RedirectView` so that we
go to the URL specified by `next`, or fall back to `profile_detail` if
for some reason the `next` parameter is missing (for example, if the
user visits `profile_follow` directly by typing
`.../profile/@<username>/follow` in their browser's URL bar).

## Feeds

We need to go back all the way to the beginning for this one.

In `articles/views.py`, we need to modify our very first view, `home`,
so that it can give us a feed of articles written by users we follow:

``` { .python hl_lines="6-11" }
class Home(TemplateView):
    # ...
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["global_feed"] = Article.objects.order_by("-created_at")
        if self.request.user.is_authenticated:                      # new from here
            context["your_articles"] = Article.objects.filter(
                author__in=self.request.user.profile.follows.all()
            ).order_by("-created_at")
        else:
            context["your_articles"] = None                         # new to here
        return context
```

In `templates/home.html`:

``` { .html hl_lines="4-44" }
<div class="container page">
  <div class="row">
    <div class="col-md-9">
      <div class="feed-toggle">                 <!-- new from here-->
        <ul class="nav nav-pills outline-active">
          <li class="nav-item">
            {% url 'home' as home %}
            <a
              href="{{ home }}"
              rel="prefetch"
              class="nav-link
                     {% if request.path == home %}active{% endif %}"
            >
              Global Feed
            </a>
          </li>
          {% if user.is_authenticated %}
            <li class="nav-item">
              {% url 'home_feed' as home_feed %}
              <a
                href="{{ home_feed }}"
                rel="prefetch"
                class="nav-link
                       {% if request.path == home_feed %}active{% endif %}"
              >
                Your Feed
              </a>
            </li>
          {% else %}
            <li class="nav-item">
              <a href="{% url 'login' %}" rel="prefetch" class="nav-link">
                Sign in to see your Feed
              </a>
            </li>
          {% endif %}
        </ul>
      </div>
      {% if request.path == home %}
        {% include 'article_list.html' with articles=your_articles %}
      {% elif request.path == home_feed %}
        {% include 'article_list.html' with articles=global_feed %}
      {% endif %}                               <!-- new to here -->
    </div>
  </div>
</div>
```

In `articles/urls.py`:

``` { .python }
urlpatterns = [
    # ...
    path("feed", Home.as_view(), name="home_feed"),
]
```

