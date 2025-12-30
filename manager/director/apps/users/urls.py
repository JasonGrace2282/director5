from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("guidelines/", views.accept_guidelines, name="accept_guidelines"),
    path("banned/", views.banned_view, name="banned"),
]
