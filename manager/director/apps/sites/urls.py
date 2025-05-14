from django.urls import path

from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_site, name="create"),
    path("delete/<int:site_id>", views.delete_site, name="delete"),
    path("docker/build/<int:site_id>", views.build_docker_image, name="build_docker_image"),
]
