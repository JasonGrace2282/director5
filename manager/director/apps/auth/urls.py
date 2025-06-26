from django.urls import path

from . import views
from .views import HTMXLoginView

app_name = "auth"

urlpatterns = [
    path("login/", HTMXLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
