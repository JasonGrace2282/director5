from django.urls import path

from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_site, name="create"),
]
