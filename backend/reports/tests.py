from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, Staff, User
from catalog.models import Author, Book, Publisher
from circulation.models import Loan
from inventory.models import BookCopy, Location


class ReportsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.librarian_user = User.objects.create_user(
            email="librarian-reports@example.com",
            password="strong-pass-123",
            first_name="Lib",
            last_name="Reports",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.librarian = Staff.objects.create(
            user=self.librarian_user,
            role=Role.LIBRARIAN,
        )
        self.reader_user = User.objects.create_user(
            email="reader-reports@example.com",
            password="strong-pass-123",
            first_name="Read",
            last_name="Reports",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-REP-001",
            phone_number="+79990000040",
            email="reader-reports-profile@example.com",
            address="Reports St 1",
        )
        self.author = Author.objects.create(first_name="Rep", last_name="Author")
        self.publisher = Publisher.objects.create(name="Rep Publisher")
        self.book = Book.objects.create(
            title="Report Book A",
            publisher=self.publisher,
            isbn="9780000000001",
            year=2020,
            language="ru",
            description="x",
        )
        self.book.authors.add(self.author)
        self.location = Location.objects.create(name="Rep Hall", code="REP-H1")
        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-REP-0001",
            location=self.location,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )
        issue_date = date.today() - timedelta(days=5)
        self.loan = Loan.objects.create(
            copy=self.copy,
            reader=self.reader,
            issued_by=self.librarian,
            issue_date=issue_date,
            due_date=issue_date + timedelta(days=14),
            status=Loan.Status.RETURNED,
            return_date=issue_date + timedelta(days=7),
        )

    def test_librarian_can_access_top_books(self):
        self.client.force_authenticate(user=self.librarian_user)
        response = self.client.get("/api/reports/top_books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        titles = {row.get("copy__book__title") for row in response.data}
        self.assertIn("Report Book A", titles)

    def test_librarian_can_access_top_books_with_date_filter(self):
        self.client.force_authenticate(user=self.librarian_user)
        d_from = (self.loan.issue_date - timedelta(days=1)).isoformat()
        d_to = (self.loan.issue_date + timedelta(days=1)).isoformat()
        response = self.client.get(
            f"/api/reports/top_books/?from={d_from}&to={d_to}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(row.get("loan_count", 0) >= 1 for row in response.data))

    def test_librarian_can_access_overdues(self):
        self.client.force_authenticate(user=self.librarian_user)
        response = self.client.get("/api/reports/overdues/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_librarian_can_access_stock(self):
        self.client.force_authenticate(user=self.librarian_user)
        response = self.client.get("/api/reports/stock/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total", response.data)
        self.assertIn("by_status", response.data)
        self.assertGreaterEqual(response.data["total"], 1)

    def test_reader_forbidden_on_reports(self):
        self.client.force_authenticate(user=self.reader_user)
        for path in (
            "/api/reports/top_books/",
            "/api/reports/overdues/",
            "/api/reports/stock/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_forbidden(self):
        response = self.client.get("/api/reports/stock/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
