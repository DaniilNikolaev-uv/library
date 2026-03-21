from django.contrib import admin
from django.utils.html import format_html

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["id", "reader_link", "copy_link", "created_at", "expires_at", "status_badge"]
    list_filter = ["status", "created_at"]
    search_fields = ["reader__user__email", "reader__user__first_name", "reader__user__last_name", "copy__inventory_number"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]

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
            "fulfilled": "#17a2b8",
            "cancelled": "#6c757d",
            "expired": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Статус"
