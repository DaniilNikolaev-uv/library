import django_filters

from .models import Loan


class LoanFilter(django_filters.FilterSet):
    reader = django_filters.NumberFilter(field_name="reader__id")
    copy = django_filters.NumberFilter(field_name="copy__id")
    status = django_filters.MultipleChoiceFilter(choices=Loan.Status.choices)
    issued_from = django_filters.DateFilter(field_name="issue_date", lookup_expr="gte")
    issued_to = django_filters.DateFilter(field_name="issue_date", lookup_expr="lte")
    due_from = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_to = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    overdue = django_filters.BooleanFilter(
        method="filter_overdue", label="Только просроченные"
    )

    class Meta:
        model = Loan
        fields = ["reader", "copy", "status"]

    def filter_overdue(self, queryset, name, value):
        from datetime import date

        if value:
            return queryset.filter(status=Loan.Status.ACTIVE, due_date__lt=date.today())
        return queryset
