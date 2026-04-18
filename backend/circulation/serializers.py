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


class LoanIssueSerializer(serializers.Serializer):
    copy = serializers.IntegerField()
    reader = serializers.IntegerField()
    loan_days = serializers.IntegerField(required=False, min_value=1, max_value=365)


class LoanReturnSerializer(serializers.Serializer):
    return_date = serializers.DateField(required=False)
    mark_lost = serializers.BooleanField(required=False, default=False)


class LoanProlongSerializer(serializers.Serializer):
    loan_days = serializers.IntegerField(required=False, min_value=1, max_value=365)
