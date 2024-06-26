# Favourites

## Introduction

What if a user wants to bookmark a masterpiece of an article and come back to it every once in a while? We'll enable our users to favourite specific articles.

## Model

The second to last feature we need is allowing users to favourite some articles, so that they are added to the user's profile for everyone to see.

In `users/models.py`:

``` { .python  }
class Profile(models.Model):
    # ...
    favorites = models.ManyToManyField(
        "articles.Article", related_name="favorited", blank=True
    )
    # ...
    def favorite(self, article):
        """Add article to Favorites"""
        self.favorites.add(article)

    def unfavorite(self, article):
        """Remove article from Favorites"""
        self.favorites.remove(article)

    def has_favorited(self, article):
        """Return True if article is in Favorites, False otherwise"""
        return self.favorites.filter(pk=article.pk).exists()
```

## ArticleFavoriteView

In `articles/views.py`:

``` { .python  }
from django.views.generic import (
    # ...
    RedirectView
)

# ...
class ArticleFavoriteView(RedirectView):
    pattern_name = "article_detail"

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get("next", None)
        if url:
            return url
        else:
            return super().get_redirect_url(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        slug_uuid = self.kwargs.get("slug_uuid", None)
        article = get_object_or_404(Article, slug_uuid=slug_uuid)
        if request.user.profile.has_favorited(article):
            request.user.profile.unfavorite(article)
        else:
            request.user.profile.favorite(article)
        return super().post(request, *args, **kwargs)
```

In `articles/urls.py`:

``` { .python  }
# ...
from django.shortcuts import redirect, get_object_or_404
from .views import (
    # ...
    ArticleFavoriteView
)

urlpatterns = [
    # ...
    path(
        "article/<slug:slug_uuid>/favorite",
        ArticleFavoriteView.as_view(),
        name="article_favorite",
    ),
]
```

## ArticleDetailView

We don't need to modify the views for this: the logic can happen in the templates.

In `templates/article_detail.html`:

``` { .html hl_lines="16" }
{% if user == article.author.user %}
  <span>
    <a
      href="{% url 'editor_update' slug_uuid=article.slug_uuid %}"
      class="btn btn-outline-secondary btn-sm"
    >
      <span class="ion-edit">
        Edit Article
      </span>
    </a>
    {% include 'article_delete.html' %}
  </span>
{% else %}
  <span>
    {% include 'profile_follow.html' with profile=article.author %}
    {% include 'article_favorite.html' %}           <!-- new -->
  </span>
{% endif %}
```

Create `templates/article_favorite.html`:

``` { .html  }
<form
    method="post"
    action="{% url 'article_favorite' slug_uuid=article.slug_uuid %}"
    style="display:inline"
>
  <input type="hidden" name="next" value="{{ request.path }}">
  {% csrf_token %}
  <button class="btn btn-sm action-btn
                 {% if article in user.profile.favorites.all %}
                 btn-primary
                 {% else %}
                 btn-outline-primary
                 {% endif %}"
  >
    <span class="ion-heart">
      {% if article in user.profile.favorites.all %}
        Unfavorite
      {% else %}
        Favorite
      {% endif %} Article ({{ article.favorited_by.count }})
    </span>
  </button>
</form>
```

Checking if an article is in a user's `favorites` should be done in the view (or, even better, the model) instead of the template, but we would have to change our templates' structure and write new views if we wanted to include a `Favorite` button in the `article_preview.html` template.

## ArticlePreviewView

In `templates/article_preview.html`:

``` { .html hl_lines="9-11" }
<div class="info">
    <a href="{% url 'profile_detail' username=article.author.user.username %}" class="author">
        {{ article.author.user.username }}
    </a>
    <span class="date">
        {{ article.created_at|date:"D M d Y" }}
    </span>
</div>
<div class="pull-xs-right">                 <!-- new -->
    {% include 'article_favorite.html' %}   <!-- new -->
</div>                                      <!-- new -->
```

In `templates/article_favorite.html`

``` { .html hl_lines="16 22-24" }
<form
    method="post"
    action="{% url 'article_favorite' slug_uuid=article.slug_uuid %}"
    style="display:inline"
>
  <input type="hidden" name="next" value="{{ request.path }}">
  {% csrf_token %}
  <button class="btn btn-sm action-btn
                 {% if article in user.profile.favorites.all %}
                 btn-primary
                 {% else %}
                 btn-outline-primary
                 {% endif %}"
  >
    <span class="ion-heart">
      {% if request.path|truncatechars:7 == 'article' %}  <!-- new -->
        {% if article in user.profile.favorites.all %}
          Unfavorite
        {% else %}
          Favorite
        {% endif %} Article ({{ article.favorited_by.count }})
      {% else  %}                                         <!-- new -->
        {{ article.favorited_by.count }}                  <!-- new -->
      {% endif %}                                         <!-- new -->
    </span>
  </button>
</form>
```

<figure width="600">
<img src="../assets/home - favorite - before.png" />
<figcaption>Favorite button before</figcaption>
</figure>

<figure width="600">
<img src="../assets/home - favorite.png" />
<figcaption>Favorite button after</figcaption>
</figure>

## Feeds

Now, we need to do something with this `Favorite` feature: we'll display a user's favorited articles on their profile.

In `users/views.py`:

``` { .python  }
class ProfileDetailView(DetailView):
    # ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["my_articles"] = self.object.articles.order_by("-created_at")
            context["is_following"] = self.object.is_following(self.object)
            context["favorited_articles"] = self.object.favorites.order_by("-created_at")  # new
        return context
```

In `users/urls.py`:

``` { .python  }
urlpatterns = [
    # ...
    path(
        "profile/@<str:username>/favorites",
        ProfileDetailView.as_view(),
        name="profile_favorites",
    ),
]
```

In `templates/profile_detail.html`:

``` { .html hl_lines="7-15 17-27 30 32-34" }
<div class="container">
  <div class="row">
    <div class="col-xs-12 col-md-10 offset-md-1">
      <div class="articles-toggle">
        <ul class="nav nav-pills outline-active">
          <li class="nav-item">
            {% url 'profile_detail' username=profile.user.username as profile_detail %}         <!-- new from here -->
            <a
              href="{{ profile_detail }}"
              rel="prefetch"
              class="nav-link
                     {% if request.path == profile_detail %}active{% endif %}"
            >
              My Articles
            </a>                                                                                <!-- new to here -->
          </li>
          <li class="nav-item">                                                                 <!-- new from here -->
            {% url 'profile_favorites' username=profile.user.username as profile_favorites %}
            <a
              href="{{ profile_favorites }}"
              rel="prefetch"
              class="nav-link
                     {% if request.path == profile_favorites %}active{% endif %}"
            >
              Favorited Articles
            </a>
          </li>                                                                                 <!-- new to here -->
        </ul>
      </div>
      {% if request.path == profile_detail %}                                                   <!-- new -->
        {% include 'article_list.html' with articles=my_articles %}
      {% elif request.path == profile_favorites %}                                              <!-- new -->
        {% include 'article_list.html' with articles=favorited_articles %}                      <!-- new -->
      {% endif %}                                                                               <!-- new -->
    </div>
  </div>
</div>
```

