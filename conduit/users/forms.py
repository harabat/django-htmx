from django import forms
from .models import Profile, User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "bio"]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
