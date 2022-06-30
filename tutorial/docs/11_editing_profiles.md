# Editing profiles

## Introduction

We want to allow users to modify their profile information (image, bio)
and user information (username, email, password) at the same place. That
is, we want to allow users to update two models at the same URL.
Surprisingly, this common use case is not straightforward to implement
with Django, especially if we're trying to follow good practice and use
class-based views. Take a break before continuing, as we're going to go
into the weeds here.

Cool, let's recap what we're doing. We have two models (`User` and
`Profile`), which happen to be related with a `OneToOneField`. We want
to update these models in one place. Intuitively, we'll reach for the
`UpdateView`. The problem is that `UpdateView` expects a single model.
The solution is to tell our `UpdateView` to deal with two forms.

## Forms

Let's create `users/forms.py` and define two forms, one for each model:

``` { .python }
from django import forms
from .models import Profile, User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "bio"]


class UserForm(forms.ModelForm):
    new_password = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "new_password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        user.save()
        return user
```

[`ModelForm`](https://docs.djangoproject.com/en/4.0/topics/forms/modelforms/)
allows to get a lot of model-relevant form logic for free (Django's
“batteries included” philosophy).

The `ProfileForm` is self-explanatory.

The `UserForm` is a bit more complicated. Let's go through it in detail.
We want our user to be able to update three types of information: the
username, the email, and the password. We also want to expose the
current username and email values in the template, but we don't want to
expose any information about the password. The screenshot below
clarifies what we mean here: the screenshot on the right could leak
information about the number of characters in our user's password, even
though the characters themselves are masked, while the screenshot on the
right exposes no information about the password.

<figure>
<img src="../assets/settings - password field.png" width="200"
alt="Password field with masked characters" />
<figcaption aria-hidden="true">Password field with masked
characters</figcaption>
</figure>

<figure>
<img src="../assets/settings.png" width="200"
alt="Empty password field" />
<figcaption aria-hidden="true">Empty password field</figcaption>
</figure>

We want the password field in our future template to be empty, and we
don't want to force the user to type it out every time they want to
modify some other information. In other words, we want the password
field to be optional, i.e. `required=False`. Furthermore, since this
password field doesn't need any information about the current password,
we can just create a dummy `new_password` field, instead of linking our
form to the `User` model's actual `password` attribute. Finally, when we
save the form, we only want to update the password if the user has
actually changed it on the form, so we need to override the form's
`save` method. Also, because Django saves hashes of passwords, instead
of the raw password strings, in its database, we need to use the `User`
object's `set_password` method, which takes care of the password
hashing.

## Views

Now that our forms are ready, let's create the view. As we said earlier,
the intuitive choice here is the generic `UpdateView` class-based view.

``` { .python }
# ...
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# ...
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "settings.html"
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = UserForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        profile_form = self.form_class(request.POST, instance=request.user.profile)
        user_form = UserForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)
```

Again, this is a significant amount of code, so let's go through it
slowly.

Only logged-in users should be able to edit their profile information,
hence the `LoginRequiredMixin`.

`UpdateView` expects to deal with a single form by default, and every
form requires a queryset, and some explicitly-defined `fields` or
`form_class`. However, we want our `UpdateView` to deal with two forms:
we will pass one form to the view in the way it expects, and the other
we will pass as extra context data. We tell our `UpdateView` that its
(official) form will be of the class `ProfileForm` and that its queryset
will be a single instance of the `Profile` model: namely, the users will
only be able to update their own profile (hence the `get_object`
override). The additional form that `ProfileUpdateView` needs to deal
with will be of class `UserForm` and will have `self.request.user` as
its queryset. We also tell `ProfileUpdateView` that we'll want to refer
to this form by `user_form` in our template. Finally, we need to process
the two forms, which means that we need to override `UpdateView`'s
`post` method. We take our whole `POST` request and run it through both
`ProfileForm` and `UserForm`: this means that we let the forms take in
the whole of the data, pick what they need (i.e. what corresponds to
their fields), and apply it to the relevant objects. If our forms are
valid, we can save the information. Otherwise, we reject the input (and
re-render everything with relevant error information).

## Templates

In `templates/settings.html`:

``` { .html }
{% extends 'base.html' %}
{% block title %}
  <title>Settings - Conduit</title>
{% endblock %}
{% block content %}
  <div class="settings-page">
    <div class="container page">
      <div class="row">
        <div class="col-md-6 offset-md-3 col-xs-12">
          <h1 class="text-xs-center">Your Settings</h1>
          <form method="post">
            {% csrf_token %}
            <fieldset>
              <fieldset class="form-group">
                <input
                  class="form-control"
                  type="text"
                  placeholder="URL of profile picture"
                  name="{{ form.image.name }}"
                  value="{{ form.image.value|default_if_none:'' }}"
                />
              </fieldset>
              {{ form.image.errors }}
              <fieldset class="form-group">
                <input
                  class="form-control form-control-lg"
                  type="text"
                  required
                  placeholder="Username"
                  name="{{ user_form.username.name }}"
                  value="{{  user_form.username.value|default_if_none:'' }}"
                />
              </fieldset>
              {{ user_form.username.errors }}
              <fieldset class="form-group">
                <textarea
                  class="form-control form-control-lg"
                  rows="8"
                  placeholder="Short bio about you"
                  name="{{ form.bio.name }}"
                >{{ form.bio.value|default_if_none:'' }}</textarea>
              </fieldset>
              {{ form.bio.errors }}
              <fieldset class="form-group">
                <input
                  class="form-control form-control-lg"
                  type="email"
                  placeholder="Email"
                  required
                  name="{{ user_form.email.name }}"
                  value="{{ user_form.email.value|default_if_none:'' }}"
                />
              </fieldset>
              {{ user_form.email.errors }}
              <fieldset class="form-group">
                <input
                  class="form-control form-control-lg"
                  type="password"
                  placeholder="New Password"
                  name="{{ user_form.new_password.name }}"
                />
              </fieldset>
              {{ user_form.new_password.errors }}
              <button class="btn btn-lg btn-primary pull-xs-right" type="submit">
                Update Settings
              </button>
            </fieldset>
          </form>
          <hr />
          <a href="{% url 'logout' %}" class="btn btn-outline-danger">
            Or click here to logout.
          </a>
        </div>
      </div>
    </div>
  </div>
{% endblock %}
```

The template is quite simple, for a change: we refer to the
`ProfileUpdateView`'s main form by `form`, and to the additional form by
`user_form`.

Finally, let's specify a URL to `settings` and add a link in the navbar
and in each individual profile.

In `users/urls.py`:

``` { .python }
# ...
from .views import Login, Logout, SignUpView, ProfileDetailView, ProfileUpdateView


urlpatterns = [
    # ...
    path("settings/", ProfileUpdateView.as_view(), name="settings"),
]
```

In `templates/nav.html`:

``` { .html }
<li class="nav-item">
  <a rel="prefetch" href="{% url 'editor_create' %}" class="nav-link">
    <span class="ion-compose"> New Post </span>
  </a>
</li>
<li class="nav-item">
  {% url 'settings' as settings %}
  <a
    href="{{ settings }}"
    rel="prefetch"
    class="nav-link
           {% if request.path == settings %}active{% endif %}"
  >
    <span class="ion-gear-a"> Settings </span>
  </a>
</li>
<li class="nav-item">
  <a rel="prefetch" href="{% url 'profile_detail' username=user.username %}" class="nav-link">
    <img src="{{ user.profile.image }}" class="user-pic" alt="{{ user.username }}">
    {{ user.username }}
  </a>
</li>
```

In `templates/profile_detail.html`:

``` { .html hl_lines="5-14" }
<div class="col-xs-12 col-md-10 offset-md-1">
  <img src="{{ profile.image }}" class="user-img" alt="{{ profile.user.username }}" />
  <h4>{{ profile.user.username }}</h4>
  <p>{{ profile.bio|default:"This user doesn't have a bio for now" }}</p>
  {% if user.username == profile.user.username %}   <!-- new from here -->
    <a
      href="{% url 'settings' %}"
      class="btn btn-sm btn-outline-secondary action-btn"
    >
      <span class="ion-gear-a">
        Edit Profile Settings
      </span>
    </a>
  {% endif %}                                       <!-- new to here -->
</div>
```

We should add that all of this would have been much easier if we had a
single model dealing with `User` and `Profile` information, instead of
separating the two (as we could have kept a generic `UpdateView`), but
that would have gone against best practice. Similarly, our task would
have been simplified if `User` and `Profile` were related through a
`ForeignKey` (as we could have used [inline
formsets](https://docs.djangoproject.com/en/4.0/topics/forms/modelforms/#inline-formsets)),
but that would have gone against common patterns in Django.

