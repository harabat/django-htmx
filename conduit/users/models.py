from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.urls import reverse
from django.db import models


class CustomUserManager(UserManager):
    """custom UserManager with unique identifier is email instead of username"""

    def create_user(self, email, username, password=None):
        """Create and return a User with username, email, and password"""

        if email is None:
            raise ValueError("Email is required.")
        if username is None:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password=None):
        """Create and return a SuperUser with admin permissions."""

        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        return user


class User(AbstractUser):
    """User model"""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Profile model"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.URLField(
        default="https://static.productionready.io/images/smiley-cyrus.jpg"
    )
    bio = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"username": self.user.username})
