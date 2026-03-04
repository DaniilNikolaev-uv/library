from rest_framework import serializers

from .models import BookCopy, Location


class LocationSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ["id", "name", "code", "parent", "full_path", "children_count"]

    def get_children_count(self, obj):
        return obj.children.count()


class LocationShortSerializer(serializers.ModelSerializer):
    full_path = serializers.CharField(read_only=True)

    class Meta:
        model = Location
        fields = ["id", "code", "name", "full_path"]


# ── BookCopy ────────────────────────────────────────────────────────────────


class BookCopyListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    location_display = LocationShortSerializer(source="location", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BookCopy
        fields = [
            "id",
            "book",
            "book_title",
            "inventory_number",
            "barcode",
            "location",
            "location_display",
            "status",
            "status_display",
            "acquired_date",
            "writeoff_date",
            "notes",
        ]


class BookCopyDetailSerializer(BookCopyListSerializer):
    class Meta(BookCopyListSerializer.Meta):
        fields = BookCopyListSerializer.Meta.fields + ["created_at", "updated_at"]


class BookCopyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = [
            "book",
            "inventory_number",
            "barcode",
            "location",
            "status",
            "acquired_date",
            "writeoff_date",
            "notes",
        ]

    def validate(self, attrs):
        status = attrs.get("status", BookCopy.Status.AVAILABLE)
        writeoff_date = attrs.get("writeoff_date")

        if status == BookCopy.Status.WRITTEN_OFF and not writeoff_date:
            raise serializers.ValidationError(
                {"writeoff_date": "Укажите дату списания для статуса «Списан»."}
            )
        if status != BookCopy.Status.WRITTEN_OFF and writeoff_date:
            raise serializers.ValidationError(
                {"writeoff_date": "Дата списания — только для статуса «Списан»."}
            )
        return attrs


class BookCopyStatusSerializer(serializers.Serializer):
    """Только для PATCH /copies/{id}/status/"""

    status = serializers.ChoiceField(choices=BookCopy.Status.choices)
    writeoff_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == BookCopy.Status.WRITTEN_OFF and not attrs.get(
            "writeoff_date"
        ):
            raise serializers.ValidationError(
                {"writeoff_date": "Укажите дату списания."}
            )
        return attrs
