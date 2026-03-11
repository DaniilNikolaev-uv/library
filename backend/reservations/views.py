from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Reservation
from .permissions import IsStaff, IsStaffOrOwner
from .serializers import CreateReservationSerializer, ReservationSerializer
from .services import ReservationError, cancel_reservation, create_reservation


class ReservationViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Reservation.objects.select_related("reader__user", "copy__book").all()
    serializer_class = ReservationSerializer
    permission_classes = [IsStaffOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "copy", "reader"]
    search_fields = ["copy__inventory_number", "copy__book__title", "reader__user__email"]
    ordering_fields = ["created_at", "expires_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs
        user = self.request.user
        from accounts.models import Role

        if user.role == Role.READER:
            try:
                return qs.filter(reader=user.reader)
            except Exception:
                return qs.none()
        return qs

    @action(detail=False, methods=["post"], permission_classes=[IsStaffOrOwner])
    def create_reservation(self, request):
        serializer = CreateReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reader = request.user.reader
        except Exception:
            return Response(
                {"detail": "Профиль читателя не найден."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            reservation = create_reservation(
                copy_id=serializer.validated_data["copy_id"], reader=reader
            )
        except ReservationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # audit
        try:
            from audit.models import AuditAction
            from audit.services import audit_log

            audit_log(
                user=request.user,
                action=AuditAction.RESERVE,
                entity=reservation,
                data_after={"copy_id": reservation.copy_id, "reader_id": reservation.reader_id},
            )
        except Exception:
            pass

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsStaffOrOwner])
    def cancel(self, request, pk=None):
        try:
            reservation = cancel_reservation(
                reservation_id=pk, cancelled_by_user=request.user
            )
        except ReservationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from audit.models import AuditAction
            from audit.services import audit_log

            audit_log(
                user=request.user,
                action=AuditAction.CANCEL_RESERVATION,
                entity=reservation,
                data_after={"status": reservation.status},
            )
        except Exception:
            pass

        return Response(ReservationSerializer(reservation).data)

    @action(detail=False, methods=["get"], permission_classes=[IsStaffOrOwner])
    def my(self, request):
        try:
            reader = request.user.reader
        except Exception:
            return Response({"detail": "Профиль читателя не найден."}, status=404)
        qs = self.get_queryset().filter(reader=reader).order_by("-created_at")
        return Response(ReservationSerializer(qs, many=True).data)
