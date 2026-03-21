from django.contrib import admin
from django.utils.html import format_html

from .models import AuditLog, AuditAction


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user_link", "action", "entity_type", "entity_id"]
    list_filter = ["action", "entity_type", "timestamp"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "entity_id"]
    ordering = ["-timestamp"]
    readonly_fields = ["user", "entity_type", "entity_id", "action", "timestamp", "data_before", "data_after", "meta"]

    def user_link(self, obj):
        if not obj.user_id:
            return "—"
        url = f"/admin/accounts/user/{obj.user_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.user)
    user_link.short_description = "Пользователь"
