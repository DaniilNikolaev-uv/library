from rest_framework import viewsets
from reservations.models import Reservation
from reservations.serializers import ReservationSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().order_by("-id")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
