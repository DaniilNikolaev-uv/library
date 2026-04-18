from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, Staff, User
from catalog.models import Author, Book, Publisher
from circulation.models import Loan
from fines.models import Fine
from inventory.models import BookCopy, Location


class FineApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin-fines@example.com",
            password="strong-pass-123",
            first_name="Admin",
            last_name="Fines",
            role=Role.ADMIN,
            is_staff=True,
        )
        self.librarian_user = User.objects.create_user(
            email="librarian-fines@example.com",
            password="strong-pass-123",
            first_name="Librarian",
            last_name="Fines",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.librarian = Staff.objects.create(
            user=self.librarian_user,
            role=Role.LIBRARIAN,
        )

        self.reader_user = User.objects.create_user(
            email="reader-fines@example.com",
            password="strong-pass-123",
            first_name="Reader",
            last_name="Fines",
            role=Role.READER,
        )
        self.other_reader_user = User.objects.create_user(
            email="other-reader-fines@example.com",
            password="strong-pass-123",
            first_name="Other",
            last_name="Reader",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-FINES-001",
            phone_number="+79990000030",
            email="reader-fines-profile@example.com",
            address="Fines Street 1",
        )
        self.other_reader = Reader.objects.create(
            user=self.other_reader_user,
            card_number="CARD-FINES-002",
            phone_number="+79990000031",
            email="other-reader-fines-profile@example.com",
            address="Fines Street 2",
        )

        self.author = Author.objects.create(first_name="Fine", last_name="Author")
        self.publisher = Publisher.objects.create(name="Fine Publisher")
        self.book = Book.objects.create(
            title="Fine Book",
            publisher=self.publisher,
            isbn="978-0-00-000001-5",
            year=2001,
            language="ru",
            description="Fine test book",
        )
        self.book.authors.add(self.author)
        self.location = Location.objects.create(name="Fine Hall", code="FINE-HALL")

        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-FINE-0001",
            location=self.location,
            status=BookCopy.Status.ON_LOAN,
            acquired_date=date.today(),
        )
        self.other_copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-FINE-0002",
            location=self.location,
            status=BookCopy.Status.ON_LOAN,
            acquired_date=date.today(),
        )

        self.loan = Loan.objects.create(
            copy=self.copy,
            reader=self.reader,
            issued_by=self.librarian,
            due_date=date.today() - timedelta(days=10),
            status=Loan.Status.OVERDUE,
        )
        self.other_loan = Loan.objects.create(
            copy=self.other_copy,
            reader=self.other_reader,
            issued_by=self.librarian,
            due_date=date.today() - timedelta(days=8),
            status=Loan.Status.OVERDUE,
        )

        self.fine = Fine.objects.create(
            loan=self.loan,
            amount=Decimal("100.00"),
            paid_amount=Decimal("0.00"),
            status=Fine.Status.UNPAID,
        )
        self.other_fine = Fine.objects.create(
            loan=self.other_loan,
            amount=Decimal("120.00"),
            paid_amount=Decimal("0.00"),
            status=Fine.Status.UNPAID,
        )

    def test_reader_sees_only_own_fines(self):
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get("/api/fines/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.fine.id)

    def test_staff_can_pay_fine(self):
        self.client.force_authenticate(user=self.librarian_user)
        response = self.client.post(
            f"/api/fines/{self.fine.id}/pay/",
            {"amount": "40.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.fine.refresh_from_db()
        self.assertEqual(self.fine.paid_amount, Decimal("40.00"))
        self.assertEqual(self.fine.status, Fine.Status.PARTIALLY_PAID)

    def test_reader_cannot_pay_fine(self):
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.post(
            f"/api/fines/{self.fine.id}/pay/",
            {"amount": "10.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
