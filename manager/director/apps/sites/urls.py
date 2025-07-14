from django.urls import path

from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_site_view, name="create"),
    path("create-basic/", views.create_site_view_basic_form, name="create_basic"),
    path("delete/<int:site_id>", views.delete_site, name="delete"),
]
