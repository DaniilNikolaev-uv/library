from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Role
from reservations.models import Reservation
from reservations.permissions import IsStaffOrOwner
from reservations.serializers import ReservationSerializer
from reservations.services import ReservationError, cancel_reservation, create_reservation


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().order_by("-id")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsStaffOrOwner]

    def get_queryset(self):
        qs = super().get_queryset().select_related("reader__user", "copy__book")
        if getattr(self, "swagger_fake_view", False):
            return qs
        if self.request.user.role in (Role.ADMIN, Role.LIBRARIAN):
            return qs
        try:
            return qs.filter(reader__user=self.request.user)
        except Exception:
            return qs.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reader = None
        if request.user.role in (Role.ADMIN, Role.LIBRARIAN):
            reader = serializer.validated_data["reader"]
        else:
            reader = getattr(request.user, "reader", None)
            if reader is None:
                return Response(
                    {"detail": "Профиль читателя не найден."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            reservation = create_reservation(
                copy_id=serializer.validated_data["copy"].id,
                reader=reader,
            )
        except ReservationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def my(self, request):
        """
        Брони текущего пользователя (читателя).

        Нужен для фронтенда: GET /api/reservations/my/
        """
        reader = getattr(request.user, "reader", None)
        if reader is None:
            return Response([], status=status.HTTP_200_OK)
        qs = (
            Reservation.objects.filter(reader=reader)
            .select_related("reader__user", "copy__book")
            .order_by("-id")
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = ReservationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(ReservationSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        try:
            reservation = cancel_reservation(
                reservation_id=int(pk),
                cancelled_by_user=request.user,
            )
        except ReservationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReservationSerializer(reservation).data)
