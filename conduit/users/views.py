from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User


class Login(LoginView):
    template_name = "login.html"


class Logout(LogoutView):
    template_name = "logout.html"


class SignUpView(CreateView):
    model = User
    template_name = "signup.html"
    success_url = reverse_lazy("home")
