from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, Staff, User
from catalog.models import Author, Book, Publisher
from circulation.models import Loan
from circulation.services import issue_book, return_book
from inventory.models import BookCopy, Location


class CirculationServiceTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            email="librarian@example.com",
            password="strong-pass-123",
            first_name="Lib",
            last_name="Rarian",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.staff = Staff.objects.create(user=self.staff_user, role=Role.LIBRARIAN)

        self.reader_user = User.objects.create_user(
            email="reader@example.com",
            password="strong-pass-123",
            first_name="Read",
            last_name="Er",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-001",
            phone_number="+79990000000",
            email="reader-profile@example.com",
            address="Test Street 1",
        )

        self.author = Author.objects.create(first_name="Leo", last_name="Tolstoy")
        self.publisher = Publisher.objects.create(name="Classic House")
        self.book = Book.objects.create(
            title="War and Peace",
            publisher=self.publisher,
            isbn="978-0-00-000001-1",
            year=1869,
            language="ru",
            description="Classic",
        )
        self.book.authors.add(self.author)

        self.location = Location.objects.create(name="Main Hall", code="HALL-1")
        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-0001",
            location=self.location,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )

    def test_issue_book_marks_copy_on_loan(self):
        loan = issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        self.copy.refresh_from_db()
        self.assertEqual(loan.status, Loan.Status.ACTIVE)
        self.assertEqual(loan.issued_by_id, self.staff.id)
        self.assertEqual(self.copy.status, BookCopy.Status.ON_LOAN)

    def test_return_book_marks_copy_available(self):
        loan = issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        returned = return_book(loan_id=loan.id, staff=self.staff)
        self.copy.refresh_from_db()

        self.assertEqual(returned.status, Loan.Status.RETURNED)
        self.assertIsNotNone(returned.return_date)
        self.assertEqual(self.copy.status, BookCopy.Status.AVAILABLE)


class CirculationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            email="librarian-api@example.com",
            password="strong-pass-123",
            first_name="Api",
            last_name="Librarian",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.staff = Staff.objects.create(user=self.staff_user, role=Role.LIBRARIAN)
        self.reader_user = User.objects.create_user(
            email="reader-api@example.com",
            password="strong-pass-123",
            first_name="Api",
            last_name="Reader",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-API-001",
            phone_number="+79990000010",
            email="reader-api-profile@example.com",
            address="Test Street 10",
        )
        self.author = Author.objects.create(first_name="Nikolai", last_name="Gogol")
        self.publisher = Publisher.objects.create(name="API Publisher")
        self.book = Book.objects.create(
            title="Dead Souls",
            publisher=self.publisher,
            isbn="978-0-00-000001-3",
            year=1842,
            language="ru",
            description="Classic",
        )
        self.book.authors.add(self.author)
        self.location = Location.objects.create(name="Api Hall", code="API-HALL")
        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-API-0001",
            location=self.location,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )
        self.client.force_authenticate(user=self.staff_user)

    def test_issue_endpoint_creates_active_loan(self):
        response = self.client.post(
            "/api/circulation/loans/issue/",
            {"copy": self.copy.id, "reader": self.reader.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Loan.Status.ACTIVE)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.ON_LOAN)

    def test_return_and_prolong_endpoints(self):
        loan = issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        prolong_response = self.client.post(
            f"/api/circulation/loans/{loan.id}/prolong/",
            {"loan_days": 10},
            format="json",
        )
        self.assertEqual(prolong_response.status_code, status.HTTP_200_OK)
        self.assertEqual(prolong_response.data["renewals_count"], 1)

        return_response = self.client.post(
            f"/api/circulation/loans/{loan.id}/return_book/",
            {},
            format="json",
        )
        self.assertEqual(return_response.status_code, status.HTTP_200_OK)
        self.assertEqual(return_response.data["status"], Loan.Status.RETURNED)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.AVAILABLE)

    def test_reader_can_list_own_loans_via_my_endpoint(self):
        issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get("/api/circulation/loans/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reader"], self.reader.id)

    def test_staff_can_get_issue_options(self):
        response = self.client.get("/api/circulation/loans/issue_options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["readers"]), 1)
        self.assertEqual(response.data["readers"][0]["id"], self.reader.id)
        self.assertEqual(response.data["readers"][0]["card_number"], self.reader.card_number)
        self.assertEqual(len(response.data["copies"]), 1)
        self.assertEqual(response.data["copies"][0]["id"], self.copy.id)
        self.assertEqual(
            response.data["copies"][0]["inventory_number"],
            self.copy.inventory_number,
        )

    def test_reader_cannot_get_issue_options(self):
        self.client.force_authenticate(user=self.reader_user)

        response = self.client.get("/api/circulation/loans/issue_options/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_without_staff_profile_can_issue_book(self):
        fallback_user = User.objects.create_user(
            email="librarian-no-profile@example.com",
            password="strong-pass-123",
            first_name="No",
            last_name="Profile",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.client.force_authenticate(user=fallback_user)

        response = self.client.post(
            "/api/circulation/loans/issue/",
            {"copy": self.copy.id, "reader": self.reader.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Staff.objects.filter(user=fallback_user, role=Role.LIBRARIAN).exists())

    def test_staff_can_get_return_options(self):
        loan = issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        response = self.client.get("/api/circulation/loans/return_options/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["loans"]), 1)
        self.assertEqual(response.data["loans"][0]["id"], loan.id)
        self.assertEqual(response.data["loans"][0]["book_title"], self.book.title)
        self.assertEqual(
            response.data["loans"][0]["reader_card_number"],
            self.reader.card_number,
        )

    def test_staff_can_get_dashboard_stats(self):
        issue_book(copy_id=self.copy.id, reader_id=self.reader.id, staff=self.staff)

        response = self.client.get("/api/circulation/loans/dashboard_stats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["users"], 2)
        self.assertEqual(response.data["books"], 1)
        self.assertEqual(response.data["readers"], 1)
        self.assertEqual(response.data["active_loans"], 1)
