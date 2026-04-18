from datetime import date, datetime

from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from circulation.models import Loan
from inventory.models import BookCopy

from .permissions import IsStaff


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


class ReportsViewSet(viewsets.ViewSet):
    permission_classes = [IsStaff]

    @action(detail=False, methods=["get"])
    def top_books(self, request):
        """
        GET /api/reports/top_books/?from=YYYY-MM-DD&to=YYYY-MM-DD
        """
        from_date = _parse_date(request.query_params.get("from"))
        to_date = _parse_date(request.query_params.get("to"))

        qs = Loan.objects.select_related("copy__book").all()
        if from_date:
            qs = qs.filter(issue_date__gte=from_date)
        if to_date:
            qs = qs.filter(issue_date__lte=to_date)

        data = (
            qs.values("copy__book_id", "copy__book__title")
            .annotate(loan_count=Count("id"))
            .order_by("-loan_count")[:50]
        )
        return Response(list(data))

    @action(detail=False, methods=["get"])
    def overdues(self, request):
        """
        GET /api/reports/overdues/?date=YYYY-MM-DD
        """
        at_date = _parse_date(request.query_params.get("date")) or date.today()
        qs = Loan.objects.select_related("reader__user", "copy__book").filter(
            Q(status=Loan.Status.OVERDUE) | (Q(status=Loan.Status.ACTIVE) & Q(due_date__lt=at_date))
        )
        data = [
            {
                "loan_id": loan.id,
                "reader": str(loan.reader),
                "reader_email": getattr(loan.reader.user, "email", ""),
                "inventory_number": loan.copy.inventory_number,
                "book_title": loan.copy.book.title,
                "issue_date": loan.issue_date,
                "due_date": loan.due_date,
                "status": loan.status,
            }
            for loan in qs.order_by("due_date")[:500]
        ]
        return Response(data)

    @action(detail=False, methods=["get"])
    def stock(self, request):
        """
        GET /api/reports/stock/
        """
        qs = BookCopy.objects.all()
        by_status = (
            qs.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        total = qs.count()
        return Response({"total": total, "by_status": list(by_status)})

