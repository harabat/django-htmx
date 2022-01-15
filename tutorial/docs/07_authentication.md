# Authentication

## Auth views

In `users/views.py`, we take advantage of the generic `LoginView`,
`LogoutView`, and `CreateView` to implement our authentication logic:

``` python
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User


class Login(LoginView):
    template_name = "login.html"
    next_page = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.next_page)
        return super().get(request, *args, **kwargs)


class Logout(LogoutView):
    next_page = reverse_lazy("home")


class SignUpView(CreateView):
    model = User
    fields = ["username", "email", "password"]
    template_name = "signup.html"
    success_url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
```

We don't have to specify much to the generic views, they're quite
full-featured as is. What we did here is indicate where the templates
live and where the views redirect to (the
[defaults](https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url)
are `accounts/profile` for `LoginView` and `None` for `LogoutView`). We
also overrode the `get` method in `LoginView` and `SignUpView`, so that
already authenticated users who for some reason visit the login page are
automatically redirected to the `home` URL. We didn't specify a template
for `LogoutView` because it's not necessary.

## Auth urls

Let's deal with the URL patterns now. Create `users/urls.py` and add the
following:

``` python
from django.urls import path
from .views import Login, Logout, SignUp


urlpatterns = [
    path("login", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("signup", SignUp.as_view(), name="signup"),
]
```

For every app that we create, we need to tell `config/urls.py` to look
at the patterns specified in the app's `urls.py` file:

``` python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("conduit.articles.urls")),
    path("", include("conduit.users.urls")),        # new
]
```

## Auth templates

### login.html

Let's create `login.html` in the `templates` folder:

``` html
{% extends 'base.html' %}
{% block title %}
    <title>Sign in - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
    <div class="auth-page">
        <div class="container page">
            <div class="row">
                <div class="col-md-6 offset-md-3 col-xs-12">
                    <h1 class="text-xs-center">Sign In</h1>
                    <p class="text-xs-center">
                        <a href="{% url 'signup' %}">Need an account?</a>
                    </p>
                    {{ form.non_field_errors }}
                    <form method="post">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            <input
                                class="form-control form-control-lg"
                                type="email"
                                placeholder="Email"
                                name="{{ form.username.name }}"
                            >
                            {{ form.username.errors }}
                        </fieldset>
                        <fieldset class="form-group">
                            <input
                                class="form-control form-control-lg"
                                type="password"
                                placeholder="Password"
                                name="{{ form.password.name }}"
                            >
                            {{ form.password.errors }}
                        </fieldset>
                        <button class="btn btn-lg btn-primary pull-xs-right" type="submit">
                            Sign in
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

Notice that we are using `form.username` to authenticate. I initially
was trying to work with `form.email`, because that was the field we
chose to authenticate with, but it kept throwing errors: Django didn't
see the field, didn't POST the value that I gave it, and asked for the
username every time. It took me a while, but I realised that our
username *is* the email. `form.username` is effectively querying what
the `USERNAME_FIELD` is. Not straightforward though.

### signup.html

Create `signup.html`:

``` html
{% extends 'base.html' %}
{% block title %}
    <title>Sign up - Conduit: Django + HTMX</title>
{% endblock %}
{% block content %}
    <div class="auth-page">
        <div class="container page">
            <div class="row">
                <div class="col-md-6 offset-md-3 col-xs-12">
                    <h1 class="text-xs-center">Sign up</h1>
                    <p class="text-xs-center">
                        <a href="{% url 'login' %}">Have an account?</a>
                    </p>
                    {{ form.non_field_errors }}
                    <form method="post">
                        {% csrf_token %}
                        <fieldset class="form-group">
                            <input
                                class="form-control form-control-lg"
                                type="text"
                                placeholder="Your {{ form.username.name }}"
                                name="{{ form.username.name }}"
                                value="{{ form.username.value|default_if_none:'' }}"
                            >
                        </fieldset>
                        {{ form.username.errors }}
                        <fieldset class="form-group">
                            <input
                                class="form-control form-control-lg"
                                type="email"
                                placeholder="Your {{ form.email.name }}"
                                name="{{ form.email.name }}"
                                value="{{ form.email.value|default_if_none:''  }}"
                            >
                        </fieldset>
                        {{ form.email.errors }}
                        <fieldset class="form-group">
                            <input
                                class="form-control form-control-lg"
                                type="password"
                                placeholder="Your {{ form.password.name }}"
                                name="{{ form.password.name }}"
                            >
                        </fieldset>
                        {{ form.password.errors }}
                        <button class="btn btn-lg btn-primary pull-xs-right">
                            Sign up
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

