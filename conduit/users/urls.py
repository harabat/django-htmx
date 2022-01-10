from django.urls import path
from .views import (
    Login,
    Logout,
    SignUpView,
    ProfileDetailView,
    ProfileUpdateView,
    ProfileFollowView,
)


urlpatterns = [
    path("login", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("signup", SignUpView.as_view(), name="signup"),
    path("profile/@<str:username>", ProfileDetailView.as_view(), name="profile_detail"),
    path("settings/", ProfileUpdateView.as_view(), name="settings"),
    path(
        "profile/@<str:username>/follow",
        ProfileFollowView.as_view(),
        name="profile_follow",
    ),
]
