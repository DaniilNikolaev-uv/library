from rest_framework import serializers
from reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "copy", "reader", "created_at", "expires_at", "status"]
        read_only_fields = ["id", "created_at", "expires_at", "status"]
