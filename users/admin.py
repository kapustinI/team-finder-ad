from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "name", "surname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    ordering = ("id",)
    search_fields = ("email", "name", "surname")

    fieldsets = (
        (None, {"fields": ("email", "password")} ),
        ("Personal", {"fields": ("name", "surname", "avatar", "phone", "about", "github_url")} ),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")} ),
        ("Dates", {"fields": ("last_login", "created_at")} ),
    )
    readonly_fields = ("created_at",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "phone", "password1", "password2"),
            },
        ),
    )
