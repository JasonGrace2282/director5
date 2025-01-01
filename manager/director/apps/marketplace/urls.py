from django.urls import path

from . import views

app_name = "marketplace"

urlpatterns = [
    path("store/", views.store, name="store"),
]
