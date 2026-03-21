from django.contrib import admin
from django.utils.html import format_html

from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["id", "reader_link", "copy_link", "issue_date", "due_date", "return_date", "status_badge", "issued_by"]
    list_filter = ["status", "issue_date"]
    search_fields = ["reader__user__email", "reader__user__first_name", "reader__user__last_name", "copy__inventory_number"]
    ordering = ["-issue_date"]
    readonly_fields = ["issue_date", "created_at", "updated_at"]

    def reader_link(self, obj):
        url = f"/admin/accounts/reader/{obj.reader_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.reader)
    reader_link.short_description = "Читатель"

    def copy_link(self, obj):
        url = f"/admin/inventory/bookcopy/{obj.copy_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.copy)
    copy_link.short_description = "Экземпляр"

    def status_badge(self, obj):
        colors = {
            "active": "#28a745",
            "returned": "#6c757d",
            "overdue": "#dc3545",
            "lost": "#343a40",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Статус"
