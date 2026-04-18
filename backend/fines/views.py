from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Fine, FinePolicy
from .permissions import IsAdmin, IsStaff, IsStaffOrOwner
from .serializers import FinePolicySerializer, FineSerializer, PayFineSerializer
from .services import pay_fine


class FineViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Fine.objects.select_related("loan__reader__user", "loan__copy__book").all()
    serializer_class = FineSerializer
    permission_classes = [IsStaffOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "loan", "loan__reader"]
    search_fields = ["loan__copy__inventory_number", "loan__copy__book__title", "loan__reader__user__email"]
    ordering_fields = ["created_at", "amount", "paid_amount", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs
        from accounts.models import Role

        if self.request.user.role == Role.READER:
            try:
                return qs.filter(loan__reader=self.request.user.reader)
            except Exception:
                return qs.none()
        return qs

    @action(detail=True, methods=["post"], permission_classes=[IsStaff])
    def pay(self, request, pk=None):
        serializer = PayFineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fine = self.get_object()

        try:
            fine = pay_fine(fine, serializer.validated_data["amount"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Аудит (если подключен)
        try:
            from audit.services import audit_log
            from audit.models import AuditAction

            audit_log(
                user=request.user,
                action=AuditAction.PAY_FINE,
                entity=fine,
                data_before={},
                data_after={"paid_amount": str(fine.paid_amount), "status": fine.status},
            )
        except Exception:
            pass

        return Response(FineSerializer(fine).data)


class FinePolicyViewSet(viewsets.ModelViewSet):
    queryset = FinePolicy.objects.all()
    serializer_class = FinePolicySerializer
    permission_classes = [IsAdmin]
