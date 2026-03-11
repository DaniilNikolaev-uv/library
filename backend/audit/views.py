from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import AuditLog
from .permissions import IsAdmin
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["action", "entity_type", "entity_id", "user"]
    search_fields = ["entity_type", "entity_id", "user__email"]
    ordering_fields = ["timestamp", "action", "entity_type"]
    ordering = ["-timestamp"]
