import django_filters

from .models import BookCopy, Location


class BookCopyFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(field_name="book__id")
    status = django_filters.MultipleChoiceFilter(choices=BookCopy.Status.choices)
    location = django_filters.NumberFilter(field_name="location__id")
    inventory_number = django_filters.CharFilter(lookup_expr="icontains")
    barcode = django_filters.CharFilter(lookup_expr="icontains")
    acquired_after = django_filters.DateFilter(
        field_name="acquired_date", lookup_expr="gte"
    )
    acquired_before = django_filters.DateFilter(
        field_name="acquired_date", lookup_expr="lte"
    )

    class Meta:
        model = BookCopy
        fields = ["book", "status", "location", "inventory_number", "barcode"]


class LocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    code = django_filters.CharFilter(lookup_expr="icontains")
    root_only = django_filters.BooleanFilter(field_name="parent", lookup_expr="isnull")

    class Meta:
        model = Location
        fields = ["name", "code", "parent"]
