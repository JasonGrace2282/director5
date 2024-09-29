from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "director.apps.users"
    verbose_name = "Director Users"
    label = "users"
