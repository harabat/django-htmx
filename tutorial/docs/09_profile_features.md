# Profile features

## Viewing Profiles

It's time to allow users to view their own and other users' profiles.

In `users/views.py`:

``` { .python }
# other imports
from django.views.generic import CreateView, DetailView

# other views
class ProfileDetailView(DetailView):
    model = User
    template_name = "profile_detail.html"
```

In `users/urls.py`:

``` { .python }
# other imports
from .views import Login, Logout, SignUpView, ProfileDetailView


urlpatterns = [
    # other paths
    path("profile/@<str:username>", ProfileDetailView.as_view(), name="profile_detail"),
]
```

In the `templates` folder, create `profile_detail.html`:

``` { .html }
{% extends 'base.html' %}
{% block title %}
    <title>{{ profile.user.username }} - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
    <div class="profile-page">
        <div class="user-info">
            <div class="container">
                <div class="row">
                    <div class="col-xs-12 col-md-10 offset-md-1">
                        <img src="{{ profile.image }}" class="user-img" alt="{{ profile.user.username }}" />
                        <h4>{{ profile.user.username }}</h4>
                        <p>{{ profile.bio|default:"This user doesn't have a bio for now" }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

Everything should be working now, right? Let's check by going to
`localhost:8000/profile/@admin`, for example. Welp, we're getting an
error:

<figure>
<img src="../assets/profile_detail - error.png" width="600" alt="profile_detail error" /><figcaption aria-hidden="true">profile_detail error</figcaption>
</figure>

The error tells us that our `ProfileDetailView` wants to be called with
an object primary key or a slug, while we're calling it with a
`username`. The solution is simple: we just change how the view decides
which objects to show.

We override the view's `get_object` method by adding the following to
`users/views.py`:

``` { .python hl_lines="9-12" }
# other imports
from django.shortcuts import redirect, get_object_or_404

# other views
class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile_detail.html"

    def get_object(self, queryset=None):                                  # new
        username = self.kwargs.get("username", None)                    # new
        profile = get_object_or_404(User, username=username).profile    # new
        return profile                                                  # new
```

Let's try again: we should see an actual profile page (though there
isn't much on it yet). Make sure to set a profile image for your `admin`
user, as everyone else should have a default already set.

<figure>
<img src="../assets/profile_detail.png" width="600" alt="A view of a profile, sans errors" /><figcaption aria-hidden="true">A view of a profile, sans errors</figcaption>
</figure>

## Viewing Articles written by each User

Whenever we visit a user's profile, we want to see all the articles
written by that specific user. We could make a `ListView`, but passing
the list to our `DetailView`'s context is simpler.

In `users/views.py`, override the `get_context_data` method of
`ProfileDetailView`:

``` { .python }
# other views
class ProfileDetailView(DetailView):
    # ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["my_articles"] = self.object.articles.order_by('-created_at')
        return context
```

This will return all the articles written by the user whose username is
specified in the URL: for example, `/profile/@admin` will return all the
articles written by `admin`. Technically, we could have obtained this
queryset directly in the template with something like
`{{ profile.articles.order_by|dictsortreversed:"created_at" }}`, but
dealing with logic in views makes for clearer code and easier debugging.

Expose the `article_list.html` template in
`templates/profile_detail.html`:

``` { .html hl_lines="18-33" }
{% extends 'base.html' %}
{% block title %}
    <title>{{ profile.user.username }} - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
    <div class="profile-page">
        <div class="user-info">
            <div class="container">
                <div class="row">
                    <div class="col-xs-12 col-md-10 offset-md-1">
                        <img src="{{ profile.image }}" class="user-img" alt="{{ profile.user.username }}" />
                        <h4>{{ profile.user.username }}</h4>
                        <p>{{ profile.bio|default:"This user doesn't have a bio for now" }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="container">                 <!-- new from here -->
            <div class="row">
                <div class="col-xs-12 col-md-10 offset-md-1">
                    <div class="articles-toggle">
                        <ul class="nav nav-pills outline-active">
                            <li class="nav-item">
                                <span class="nav-link">
                                  My Articles
                                </span>
                            </li>
                        </ul>
                    </div>
                    {% include 'article_list.html' with articles=my_articles %}
                </div>
            </div>
        </div>                                  <!-- new to here -->
    </div>
{% endblock %}
```

## Links to Profiles in templates

We now need to link the profile page from all the places our users'
usernames are exposed.

In `templates/article_preview.html`, change the following lines:

``` { .html hl_lines="2-4 6 8" }
<div class="article-meta">
  <a href="{% url 'profile_detail' username=article.author.user.username %}">                   <!-- new -->
    <img src="{{ article.author.image }}" alt="{{ article.author.user.username }}"/>            <!-- new -->
  </a>                                                                                          <!-- new -->
  <div class="info">
    <a href="{% url 'profile_detail' username=article.author.user.username %}" class="author">  <!-- from <span class="author"> -->
        {{ article.author.user.username }}
    </a>                                                                                        <!-- from </span> -->
    <span class="date">
      {{ article.created_at|date:"D M d Y" }}
    </span>
  </div>
</div>
```

In `templates/nav.html`:

``` { .html hl_lines="13-24" }
{% if user.is_authenticated %}
  <li class="nav-item">
    {% url 'editor_create' as editor_create %}
    <a
      href="{{ editor_create }}"
      rel="prefetch"
      class="nav-link
             {% if request.path == editor_create %}active{% endif %}"
    >
      <span class="ion-compose"> New Post </span>
    </a>
  </li>
  <li class="nav-item">                             <!-- new from here -->
    {% url 'profile_detail' username=user.username as profile %}
    <a
      href="{{ profile }}"
      rel="prefetch"
      class="nav-link
             {% if request.path == profile %}active{% endif %}"
    >
      <img src="{{ user.profile.image }}" class="user-pic" alt="{{ user.username }}">
      {{ user.username }}
    </a>
  </li>                                             <!-- new to here -->
  <li class="nav-item">
    <a rel="prefetch" href="{% url 'logout' %}" class="nav-link">
      <span class="ion-log-out"></span>
    </a>
  </li>
{% else %}
```

In `templates/article_detail.html`:

``` { .html hl_lines="2-4 6 8" }
<div class="article-meta">
  <a href="{% url 'profile_detail' username=article.author.user.username %}">                  <!-- new -->
    <img src="{{ article.author.image }}" alt="{{ article.author.user.username }}"/>           <!-- new -->
  </a>                                                                                         <!-- new -->
  <div class="info">
    <a href="{% url 'profile_detail' username=article.author.user.username %}" class="author"> <!-- from <span class="author"> -->
      {{ article.author.user.username }}
    </a>                                                                                       <!-- from </span> -->
    <span class="date">
      {{ article.created_at|date:"D M d Y" }}
    </span>
  </div>
```

In `templates/comments.html`:

``` { .html hl_lines="2-5 7" }
<div class="card-footer">
  <a href="{% url 'profile_detail' username=comment.author.user.username %}" class="comment-author">            <!-- new -->
    <img src="{{ comment.author.image }}" class="comment-author-img" alt="{{ comment.author.user.username }}"/> <!-- new -->
  </a>                                                                                                          <!-- new -->
  <a href="{% url 'profile_detail' username=comment.author.user.username %}" class="comment-author">            <!-- from <span class="comment-author"> -->
      {{ comment.author.user.username }}
  </a>                                                                                                          <!-- from </span>-->
  <span class="date-posted">
    {{ comment.created_at|date:"D M d Y" }}
  </span>
  {% include 'comment_delete.html' %}
</div>
```

