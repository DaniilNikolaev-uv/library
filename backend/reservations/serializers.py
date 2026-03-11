from rest_framework import serializers

from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reader_name = serializers.CharField(source="reader.__str__", read_only=True)
    inventory_number = serializers.CharField(
        source="copy.inventory_number", read_only=True
    )
    book_title = serializers.CharField(source="copy.book.title", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "copy",
            "inventory_number",
            "book_title",
            "reader",
            "reader_name",
            "created_at",
            "expires_at",
            "status",
            "status_display",
        ]


class CreateReservationSerializer(serializers.Serializer):
    copy_id = serializers.IntegerField()

