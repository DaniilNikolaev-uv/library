from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "copy", "reader", "status", "created_at", "expires_at")
    list_filter = ("status",)
    search_fields = ("copy__inventory_number", "reader__user__email")
    ordering = ("-created_at",)
