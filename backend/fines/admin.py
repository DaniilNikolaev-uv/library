from django.contrib import admin
from django.utils.html import format_html

from .models import Fine, FinePolicy


@admin.register(FinePolicy)
class FinePolicyAdmin(admin.ModelAdmin):
    list_display = ["daily_rate", "max_fine_per_loan", "grace_period_days", "is_active", "created_at"]
    list_filter = ["is_active"]
    ordering = ["-is_active", "-created_at"]


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ["id", "loan_link", "amount", "paid_amount", "status_badge", "calculated_at"]
    list_filter = ["status", "calculated_at"]
    search_fields = ["loan__reader__user__email", "loan__reader__user__first_name"]
    ordering = ["-created_at"]
    readonly_fields = ["calculated_at", "created_at", "updated_at"]

    def loan_link(self, obj):
        url = f"/admin/circulation/loan/{obj.loan_id}/change/"
        return format_html('<a href="{}">Loan #{}</a>', url, obj.loan_id)
    loan_link.short_description = "Выдача"

    def status_badge(self, obj):
        colors = {
            "unpaid": "#dc3545",
            "partially_paid": "#ffc107",
            "paid": "#28a745",
            "cancelled": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        text_color = "black" if obj.status == "partially_paid" else "white"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Статус"
