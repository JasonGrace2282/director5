from django.urls import path

from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/<int:site_id>", views.site_dashboard, name="dashboard"),
    path("create/", views.create_site, name="create"),
    path("delete/<int:site_id>", views.delete_site, name="delete"),
    path("delete/operations/<site_id>", views.clear_operations, name="delete_operations"),
]
