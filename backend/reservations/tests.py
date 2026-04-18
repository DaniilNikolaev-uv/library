from datetime import date

from django.test import TestCase

from accounts.models import Reader, Role, User
from catalog.models import Author, Book, Publisher
from inventory.models import BookCopy, Location
from reservations.models import Reservation
from reservations.services import cancel_reservation, create_reservation


class ReservationServiceTests(TestCase):
    def setUp(self):
        self.reader_user = User.objects.create_user(
            email="reader2@example.com",
            password="strong-pass-123",
            first_name="Read",
            last_name="Two",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-002",
            phone_number="+79990000001",
            email="reader2-profile@example.com",
            address="Test Street 2",
        )

        self.author = Author.objects.create(first_name="Fyodor", last_name="Dostoevsky")
        self.publisher = Publisher.objects.create(name="Russian Classics")
        self.book = Book.objects.create(
            title="Crime and Punishment",
            publisher=self.publisher,
            isbn="978-0-00-000001-2",
            year=1866,
            language="ru",
            description="Classic",
        )
        self.book.authors.add(self.author)

        self.location = Location.objects.create(name="Shelf A", code="A-1")
        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-0002",
            location=self.location,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )

    def test_create_reservation_sets_copy_reserved(self):
        reservation = create_reservation(copy_id=self.copy.id, reader=self.reader)

        self.copy.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.ACTIVE)
        self.assertEqual(self.copy.status, BookCopy.Status.RESERVED)

    def test_cancel_reservation_sets_copy_available(self):
        reservation = create_reservation(copy_id=self.copy.id, reader=self.reader)

        cancelled = cancel_reservation(
            reservation_id=reservation.id,
            cancelled_by_user=self.reader_user,
        )
        self.copy.refresh_from_db()

        self.assertEqual(cancelled.status, Reservation.Status.CANCELLED)
        self.assertEqual(self.copy.status, BookCopy.Status.AVAILABLE)
