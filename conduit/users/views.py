from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import User, Profile
from .forms import ProfileForm, UserForm


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
        user = get_object_or_404(User, username=username)
        return user.profile


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
            messages.success(request, "Your profile has been updated!")
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)
