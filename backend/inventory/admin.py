from django.contrib import admin

from .models import BookCopy, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "parent", "full_path"]
    list_filter = ["parent"]
    search_fields = ["name", "code"]
    ordering = ["code"]


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ["inventory_number", "book", "barcode", "location", "status", "acquired_date"]
    list_filter = ["status", "location", "book"]
    search_fields = ["inventory_number", "barcode", "book__title"]
    ordering = ["-inventory_number"]
    readonly_fields = ["created_at", "updated_at"]
