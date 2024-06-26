from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .models import Profile
from .forms import ProfileForm, UserForm


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
    model = get_user_model()
    fields = ["username", "email", "password"]
    template_name = "signup.html"
    success_url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        email = form.cleaned_data.get("email")
        authenticated_user = authenticate(email=email, password=password)
        login(self.request, authenticated_user)
        return redirect(self.success_url)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile_detail.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username", None)
        profile = get_object_or_404(get_user_model(), username=username).profile
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["my_articles"] = self.object.articles.order_by("-created_at")
            context["is_following"] = self.object.is_following(self.object)
            context["favorited_articles"] = self.object.favorites.order_by(
                "-created_at"
            )
        return context


class ProfileFollowView(LoginRequiredMixin, RedirectView):
    pattern_name = "profile_detail"

    def get_redirect_url(self, *args, **kwargs):
        url = self.request.POST.get("next", None)
        if url:
            return url
        else:
            return super().get_redirect_url(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = self.kwargs.get("username", None)
        profile = get_object_or_404(get_user_model(), username=username).profile
        if request.user.profile.is_following(profile):
            request.user.profile.unfollow(profile)
        else:
            request.user.profile.follow(profile)
        return super().post(request, *args, **kwargs)


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
