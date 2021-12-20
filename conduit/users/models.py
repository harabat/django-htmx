from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db import models


class CustomUserManager(UserManager):
    """custom UserManager with unique identifier is email instead of username"""

    def create_user(self, username, email, password=None):
        """Create and return a User with username, email, and password"""

        if email is None:
            raise ValueError("Email is required.")
        if username is None:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        """Create and return a SuperUser with admin permissions."""

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save()

        user = self.create_user(username, email, password)

        return user


class User(AbstractUser):
    """User model"""

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Profile model"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.URLField(blank=True)
