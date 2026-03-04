from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BookCopyFilter, LocationFilter
from .models import BookCopy, Location
from .permissions import IsAdminOrLibrarian
from .serializers import (
    BookCopyDetailSerializer,
    BookCopyListSerializer,
    BookCopyStatusSerializer,
    BookCopyWriteSerializer,
    LocationSerializer,
)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.select_related("parent").order_by("code")
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LocationFilter
    search_fields = ["name", "code"]
    ordering_fields = ["code", "name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAdminOrLibrarian()]

    @action(detail=True, methods=["get"])
    def copies(self, request, pk=None):
        """GET /api/locations/{id}/copies/"""
        location = self.get_object()
        qs = BookCopy.objects.filter(location=location).select_related("book")
        return Response(BookCopyListSerializer(qs, many=True).data)


class BookCopyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Нет DestroyModelMixin намеренно —
    экземпляры не удаляются, только списываются через /status/.
    """

    queryset = BookCopy.objects.select_related("book", "location").order_by(
        "inventory_number"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookCopyFilter
    search_fields = ["inventory_number", "barcode", "book__title"]
    ordering_fields = ["inventory_number", "acquired_date", "status"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookCopyDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return BookCopyWriteSerializer
        if self.action == "set_status":
            return BookCopyStatusSerializer
        return BookCopyListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAdminOrLibrarian()]

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        """
        PATCH /api/copies/{id}/status/
        Смена статуса вручную (available / lost / repair / written_off).
        on_loan и reserved — только через circulation/reservations.
        """
        copy = self.get_object()
        serializer = BookCopyStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        protected = {BookCopy.Status.ON_LOAN, BookCopy.Status.RESERVED}

        if new_status in protected:
            return Response(
                {
                    "detail": f"Статус «{new_status}» управляется системой автоматически."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        copy.status = new_status
        if "writeoff_date" in serializer.validated_data:
            copy.writeoff_date = serializer.validated_data["writeoff_date"]
        if "notes" in serializer.validated_data:
            copy.notes = serializer.validated_data["notes"]
        copy.save(update_fields=["status", "writeoff_date", "notes", "updated_at"])

        return Response(BookCopyDetailSerializer(copy).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """GET /api/copies/stats/ — количество экземпляров по каждому статусу."""
        rows = BookCopy.objects.values("status").annotate(count=Count("id"))
        result = {r["status"]: r["count"] for r in rows}
        for choice in BookCopy.Status:
            result.setdefault(choice.value, 0)
        return Response(result)
