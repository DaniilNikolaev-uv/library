from datetime import date

from django.test import TestCase

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
