from django.urls import path, include

from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_site_view, name="create"),
    path("create-basic/", views.create_site_view_basic_form, name="create_basic"),
    path("sites/delete/<int:site_id>", views.delete_site, name="delete"),
    path("sites/<int:site_id>/dashboard", views.SiteDashboard.as_view(), name="dashboard"),
    path("sites/<int:site_id>/database", views.site_database, name="database"),
    path("sites/<int:site_id>/files", views.site_file_manager, name="files_root"),
    path("sites/<int:site_id>/files/<path:subpath>", views.site_file_manager, name="files"),
    path("sites/<int:site_id>/console", views.site_console, name="console"),
    path("sites/<int:site_id>/settings", views.site_settings, name="settings"),
]
