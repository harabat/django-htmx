from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import User, Profile


class Login(LoginView):
    template_name = "login.html"
    next_page = reverse_lazy("home")


class Logout(LogoutView):
    next_page = reverse_lazy("home")


class SignUpView(CreateView):
    model = User
    fields = ["username", "email", "password"]
    template_name = "signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile_detail.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username", None)
        user = get_object_or_404(User, username=username)
        return user.profile
