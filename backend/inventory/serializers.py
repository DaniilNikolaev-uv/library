from rest_framework import serializers
from inventory.models import BookCopy, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "code", "parent", "full_path"]
        read_only_fields = ["id", "full_path"]


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = [
            "id", "book", "inventory_number", "barcode", "location",
            "status", "acquired_date", "writeoff_date", "notes"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
