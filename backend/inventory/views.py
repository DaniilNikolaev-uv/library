from rest_framework import viewsets
from inventory.models import BookCopy, Location
from inventory.serializers import BookCopySerializer, LocationSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by("code")
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.all().order_by("-id")
    serializer_class = BookCopySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
