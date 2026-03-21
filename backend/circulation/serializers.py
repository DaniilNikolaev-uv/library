from rest_framework import serializers
from circulation.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "id", "copy", "reader", "issued_by", "issue_date",
            "due_date", "return_date", "status", "renewals_count"
        ]
        read_only_fields = ["id", "issue_date", "issued_by", "status", "renewals_count"]


class LoanReturnSerializer(serializers.Serializer):
    return_date = serializers.DateField(required=False)
