from rest_framework import serializers

from .models import Loan


class LoanListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reader_name = serializers.CharField(source="reader.__str__", read_only=True)
    book_title = serializers.CharField(source="copy.book.title", read_only=True)
    inventory_number = serializers.CharField(
        source="copy.inventory_number", read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "copy",
            "inventory_number",
            "book_title",
            "reader",
            "reader_name",
            "issued_by",
            "issue_date",
            "due_date",
            "return_date",
            "return_processed_by",
            "status",
            "status_display",
            "renewals_count",
            "is_overdue",
        ]


class LoanDetailSerializer(LoanListSerializer):
    class Meta(LoanListSerializer.Meta):
        fields = LoanListSerializer.Meta.fields + ["created_at", "updated_at"]


class IssueSerializer(serializers.Serializer):
    """POST /api/loans/issue/"""

    copy_id = serializers.IntegerField()
    reader_id = serializers.IntegerField()
    loan_days = serializers.IntegerField(min_value=1, max_value=90, required=False)


class ReturnSerializer(serializers.Serializer):
    """POST /api/loans/{id}/return/"""

    mark_lost = serializers.BooleanField(default=False)


class RenewSerializer(serializers.Serializer):
    """POST /api/loans/{id}/renew/"""

    loan_days = serializers.IntegerField(min_value=1, max_value=90, required=False)
