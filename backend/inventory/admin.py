from django.contrib import admin

# from .models import BookCopy, Location


# @admin.register(Location)
# class LocationAdmin(admin.ModelAdmin):
#     list_display = ["code", "name", "parent"]
#     search_fields = ["code", "name"]
#     ordering = ["code"]


# @admin.register(BookCopy)
# class BookCopyAdmin(admin.ModelAdmin):
#     list_display = [
#         "inventory_number",
#         "barcode",
#         "book",
#         "location",
#         "status",
#         "acquired_date",
#     ]
#     list_filter = ["status", "location"]
#     search_fields = ["inventory_number", "barcode", "book__title"]
#     readonly_fields = ["created_at", "updated_at"]
