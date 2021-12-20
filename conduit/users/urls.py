from django.urls import path
from .views import Login, Logout, SignUpView


urlpatterns = [
    path("login", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("signup", SignUpView.as_view(), name="signup"),
]
