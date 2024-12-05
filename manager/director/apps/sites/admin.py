from django.contrib import admin

from .models import (
    Database,
    DatabaseHost,
    DockerAction,
    DockerImage,
    Site,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "mode", "purpose", "availability")
    list_filter = ("mode", "availability")
    search_fields = ("name",)


@admin.register(DatabaseHost)
class DatabaseHostAdmin(admin.ModelAdmin):
    list_display = ("hostname", "port", "dbms")
    list_filter = ("dbms",)
    search_fields = ("hostname",)


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("redacted_db_url", "site", "host__dbms")
    search_fields = ("host__hostname", "site__name")


@admin.register(DockerImage)
class DockerImageAdmin(admin.ModelAdmin):
    list_display = ("name", "tag", "language")
    list_filter = ("language",)
    search_fields = ("name", "tag")


@admin.register(DockerAction)
class DockerActionAdmin(admin.ModelAdmin):
    list_display = ("name", "command")
    list_filter = ("command",)
    search_fields = ("name",)
