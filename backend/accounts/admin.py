from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Reader, Staff, User

UserModel = get_user_model()


@admin.register(UserModel)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "is_active", "is_staff"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
    )


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ["user", "card_number", "phone_number", "email", "is_blocked", "date_registered"]
    list_filter = ["is_blocked", "date_registered"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "card_number"]
    ordering = ["-date_registered"]
    readonly_fields = ["date_registered"]


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["user", "role"]
    list_filter = ["role"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
