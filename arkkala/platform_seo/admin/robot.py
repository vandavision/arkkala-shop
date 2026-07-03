# admin.py
from django.contrib import admin
from platform_tools.mixins.admins import LimitOneInstanceAdminMixin

from platform_seo.admin.actions import reset_robots_txt
from platform_seo.models import RobotsTxt


@admin.register(RobotsTxt)
class RobotsTxtAdmin(LimitOneInstanceAdminMixin):
    list_display = (
        "id",
        "modified_at",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "modified_at",
    )
    actions = (reset_robots_txt,)
    ordering = ("-modified_at",)
    search_fields = ("content",)
    list_filter = (
        "modified_at",
        "created_at",
    )
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("content",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "modified_at"), "classes": ("collapse",)},
        ),
    )
