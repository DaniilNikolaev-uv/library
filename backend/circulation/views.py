from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Role
from circulation.models import Loan
from circulation.permissions import IsStaff, IsStaffOrOwner
from circulation.serializers import (
    LoanIssueSerializer,
    LoanProlongSerializer,
    LoanReturnSerializer,
    LoanSerializer,
)
from circulation.services import LOAN_DAYS, LoanError, issue_book, renew_loan, return_book


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by("-id")
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "issue", "return_book", "prolong"):
            return [IsAuthenticated(), IsStaff()]
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), IsStaffOrOwner()]
        return [IsAuthenticated(), IsStaff()]

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
        serializer = LoanIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return Response(
                {"detail": "Только сотрудник может выполнять выдачу."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            loan = issue_book(
                copy_id=serializer.validated_data["copy"],
                reader_id=serializer.validated_data["reader"],
                staff=staff,
                loan_days=serializer.validated_data.get("loan_days", LOAN_DAYS),
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def issue(self, request):
        return self.create(request)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        serializer = LoanReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return Response(
                {"detail": "Только сотрудник может принимать возврат."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            loan = return_book(
                loan_id=int(pk),
                staff=staff,
                mark_lost=serializer.validated_data.get("mark_lost", False),
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LoanSerializer(loan).data)

    @action(detail=True, methods=["post"])
    def prolong(self, request, pk=None):
        serializer = LoanProlongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = getattr(request.user, "staff_profile", None)
        if not staff:
            return Response(
                {"detail": "Только сотрудник может продлевать выдачу."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            loan = renew_loan(
                loan_id=int(pk),
                staff_or_reader=staff,
                loan_days=serializer.validated_data.get("loan_days", LOAN_DAYS),
            )
        except LoanError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LoanSerializer(loan).data)
