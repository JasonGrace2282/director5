from __future__ import annotations

from django.contrib import admin

from .models import User, Ban


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    date_hierarchy = "date_joined"
    list_display = (
        "username",
        "full_name",
        "email",
        "is_student",
        "is_teacher",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "date_joined",
        "last_login",
        "is_student",
        "is_teacher",
        "is_staff",
        "is_superuser",
    )
    ordering = ("username",)
    save_as = True
    search_fields = ("username", "full_name")

@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("user", "reason_short", "start_time", "end_time", "is_active_display")
    list_filter = ("end_time",)
    search_fields = ("user__username", "user__email", "reason")
    ordering = ("-start_time",)

    def reason_short(self, obj):
        return (obj.reason[:50] + "...") if obj.reason and len(obj.reason) > 50 else obj.reason
    reason_short.short_description = "Reason"

    def is_active_display(self, obj):
        return obj.is_active
    is_active_display.boolean = True
    is_active_display.short_description = "Active?"

    readonly_fields = ("start_time",)

    fieldsets = (
        (None, {
            "fields": ("user", "reason", "start_time", "end_time")
        }),
    )
