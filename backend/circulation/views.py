from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import LoanFilter
from .models import Loan
from .permissions import IsStaff, IsStaffOrOwner
from .serializers import (
    IssueSerializer,
    LoanDetailSerializer,
    LoanListSerializer,
    RenewSerializer,
    ReturnSerializer,
)
from .services import LoanError, issue_book, renew_loan, return_book


class LoanViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Выдачи книг.

    list/retrieve  — staff или владелец выдачи
    issue          — только staff
    return         — только staff
    renew          — только staff (читатель только запрашивает — будет в reservations/requests)
    """

    queryset = Loan.objects.select_related(
        "copy__book", "reader__user", "issued_by__user", "return_processed_by__user"
    ).order_by("-issue_date")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LoanFilter
    search_fields = [
        "reader__user__first_name",
        "reader__user__last_name",
        "copy__inventory_number",
        "copy__book__title",
    ]
    ordering_fields = ["issue_date", "due_date", "status"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LoanDetailSerializer
        return LoanListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsStaffOrOwner()]
        return [IsStaff()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Читатель видит только свои выдачи
        user = self.request.user
        from accounts.models import Role

        if user.role == Role.READER:
            try:
                qs = qs.filter(reader=user.reader)
            except Exception:
                qs = qs.none()
        return qs

    # ── POST /api/loans/issue/ ─────────────────────────────────────────────
    @action(detail=False, methods=["post"], permission_classes=[IsStaff])
    def issue(self, request):
        serializer = IssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            staff = request.user.staff
        except Exception:
            return Response(
                {"detail": "Профиль сотрудника не найден."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            loan = issue_book(
                copy_id=data["copy_id"],
                reader_id=data["reader_id"],
                staff=staff,
                **({} if "loan_days" not in data else {"loan_days": data["loan_days"]}),
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LoanDetailSerializer(loan).data, status=status.HTTP_201_CREATED)

    # ── POST /api/loans/{id}/return/ ───────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsStaff])
    def return_book(self, request, pk=None):
        serializer = ReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            staff = request.user.staff
        except Exception:
            return Response(
                {"detail": "Профиль сотрудника не найден."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            loan = return_book(
                loan_id=pk,
                staff=staff,
                mark_lost=serializer.validated_data["mark_lost"],
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LoanDetailSerializer(loan).data)

    # ── POST /api/loans/{id}/renew/ ────────────────────────────────────────
    @action(detail=True, methods=["post"], permission_classes=[IsStaff])
    def renew(self, request, pk=None):
        serializer = RenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            loan = renew_loan(
                loan_id=pk,
                staff_or_reader=request.user,
                **({} if "loan_days" not in data else {"loan_days": data["loan_days"]}),
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LoanDetailSerializer(loan).data)

    # ── GET /api/loans/my/ ─────────────────────────────────────────────────
    @action(detail=False, methods=["get"], permission_classes=[IsStaffOrOwner])
    def my(self, request):
        """Личный кабинет читателя — его активные выдачи."""
        try:
            reader = request.user.reader
        except Exception:
            return Response(
                {"detail": "Профиль читателя не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = (
            Loan.objects.filter(reader=reader)
            .select_related("copy__book")
            .order_by("-issue_date")
        )
        return Response(LoanListSerializer(qs, many=True).data)
