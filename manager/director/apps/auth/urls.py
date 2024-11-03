from django.conf import settings
from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns.append(
        path(
            "password-login/",
            LoginView.as_view(template_name="auth/password-login.html"),
            name="password_login",
        )
    )
