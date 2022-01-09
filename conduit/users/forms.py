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
