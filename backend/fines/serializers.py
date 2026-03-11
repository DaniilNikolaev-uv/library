from decimal import Decimal

from rest_framework import serializers

from circulation.models import Loan

from .models import Fine, FinePolicy


class FinePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinePolicy
        fields = [
            "id",
            "daily_rate",
            "max_fine_per_loan",
            "grace_period_days",
            "is_active",
            "created_at",
            "updated_at",
        ]


class FineSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reader_name = serializers.CharField(source="loan.reader.__str__", read_only=True)
    inventory_number = serializers.CharField(
        source="loan.copy.inventory_number", read_only=True
    )
    book_title = serializers.CharField(source="loan.copy.book.title", read_only=True)

    class Meta:
        model = Fine
        fields = [
            "id",
            "loan",
            "reader_name",
            "inventory_number",
            "book_title",
            "amount",
            "paid_amount",
            "paid_at",
            "status",
            "status_display",
            "calculated_at",
            "created_at",
            "updated_at",
        ]


class PayFineSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))

