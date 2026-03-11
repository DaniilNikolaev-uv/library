from django.contrib import admin

from .models import Fine, FinePolicy


@admin.register(FinePolicy)
class FinePolicyAdmin(admin.ModelAdmin):
    list_display = ("id", "daily_rate", "max_fine_per_loan", "grace_period_days", "is_active")
    list_filter = ("is_active",)
    ordering = ("-is_active", "-created_at")


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("id", "loan", "amount", "paid_amount", "status", "paid_at", "created_at")
    list_filter = ("status",)
    search_fields = ("loan__copy__inventory_number", "loan__reader__user__email")
    ordering = ("-created_at",)
