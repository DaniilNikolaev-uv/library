from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.models import Reader, Role, Staff
from catalog.models import Book
from inventory.models import BookCopy
from circulation.models import Loan
from circulation.permissions import IsStaff, IsStaffOrOwner
from circulation.serializers import (
    LoanIssueSerializer,
    LoanProlongSerializer,
    LoanReturnSerializer,
    LoanSerializer,
)
from circulation.services import LOAN_DAYS, LoanError, issue_book, renew_loan, return_book

User = get_user_model()


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
        staff = self._get_or_create_staff_profile(request.user)
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

    @action(detail=False, methods=["get"])
    def my(self, request):
        """
        Выдачи текущего пользователя (читателя).

        Нужен для фронтенда: GET /api/circulation/loans/my/
        """
        reader = getattr(request.user, "reader", None)
        if reader is None:
            return Response([], status=status.HTTP_200_OK)
        qs = (
            Loan.objects.filter(reader=reader)
            .select_related("reader__user", "copy__book")
            .order_by("-id")
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LoanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(LoanSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def issue(self, request):
        return self.create(request)

    @action(detail=False, methods=["get"])
    def issue_options(self, request):
        readers = list(
            Reader.objects.select_related("user")
            .order_by("user__last_name", "user__first_name", "id")
            .values(
                "id",
                "card_number",
                "email",
                "is_blocked",
                "user__first_name",
                "user__last_name",
            )
        )
        copies = list(
            BookCopy.objects.select_related("book", "location")
            .filter(status=BookCopy.Status.AVAILABLE)
            .order_by("inventory_number")
            .values(
                "id",
                "inventory_number",
                "barcode",
                "book__title",
                "book__isbn",
                "location__name",
                "location__code",
            )
        )
        return Response(
            {
                "readers": [
                    {
                        "id": reader["id"],
                        "card_number": reader["card_number"],
                        "email": reader["email"],
                        "is_blocked": reader["is_blocked"],
                        "first_name": reader["user__first_name"],
                        "last_name": reader["user__last_name"],
                    }
                    for reader in readers
                ],
                "copies": [
                    {
                        "id": copy["id"],
                        "inventory_number": copy["inventory_number"],
                        "barcode": copy["barcode"],
                        "book_title": copy["book__title"],
                        "isbn": copy["book__isbn"],
                        "location_name": copy["location__name"],
                        "location_code": copy["location__code"],
                    }
                    for copy in copies
                ],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def return_options(self, request):
        loans = list(
            Loan.objects.select_related("reader__user", "copy__book")
            .filter(status__in=[Loan.Status.ACTIVE, Loan.Status.OVERDUE])
            .order_by("-id")
            .values(
                "id",
                "status",
                "issue_date",
                "due_date",
                "reader__id",
                "reader__card_number",
                "reader__email",
                "reader__user__first_name",
                "reader__user__last_name",
                "copy__id",
                "copy__inventory_number",
                "copy__barcode",
                "copy__book__title",
                "copy__book__isbn",
            )
        )
        return Response(
            {
                "loans": [
                    {
                        "id": loan["id"],
                        "status": loan["status"],
                        "issue_date": loan["issue_date"],
                        "due_date": loan["due_date"],
                        "reader_id": loan["reader__id"],
                        "reader_card_number": loan["reader__card_number"],
                        "reader_email": loan["reader__email"],
                        "reader_first_name": loan["reader__user__first_name"],
                        "reader_last_name": loan["reader__user__last_name"],
                        "copy_id": loan["copy__id"],
                        "inventory_number": loan["copy__inventory_number"],
                        "barcode": loan["copy__barcode"],
                        "book_title": loan["copy__book__title"],
                        "isbn": loan["copy__book__isbn"],
                    }
                    for loan in loans
                ]
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def dashboard_stats(self, request):
        stats = {
            "users": User.objects.count(),
            "books": Book.objects.count(),
            "active_loans": Loan.objects.filter(
                Q(status=Loan.Status.ACTIVE) | Q(status=Loan.Status.OVERDUE)
            ).count(),
            "readers": Reader.objects.count(),
        }
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        serializer = LoanReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = self._get_or_create_staff_profile(request.user)
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
        staff = self._get_or_create_staff_profile(request.user)
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

    def _get_or_create_staff_profile(self, user):
        if not user or not user.is_authenticated:
            return None
        if user.role not in (Role.ADMIN, Role.LIBRARIAN):
            return None
        staff = getattr(user, "staff_profile", None)
        if staff:
            return staff
        staff, _ = Staff.objects.get_or_create(user=user, defaults={"role": user.role})
        return staff
