from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, Staff, User
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


class ReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = User.objects.create_user(
            email="staff-res-api@example.com",
            password="strong-pass-123",
            first_name="Staff",
            last_name="ResApi",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.staff = Staff.objects.create(user=self.staff_user, role=Role.LIBRARIAN)
        self.reader_user = User.objects.create_user(
            email="reader-res-api@example.com",
            password="strong-pass-123",
            first_name="Reader",
            last_name="ResApi",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-RES-001",
            phone_number="+79990000020",
            email="reader-res-profile@example.com",
            address="Test Street 20",
        )
        self.author = Author.objects.create(first_name="Leo", last_name="Tolstoy")
        self.publisher = Publisher.objects.create(name="Reservation Publisher")
        self.book = Book.objects.create(
            title="Anna Karenina",
            publisher=self.publisher,
            isbn="978-0-00-000001-4",
            year=1877,
            language="ru",
            description="Classic",
        )
        self.book.authors.add(self.author)
        self.location = Location.objects.create(name="Res Hall", code="RES-HALL")
        self.copy = BookCopy.objects.create(
            book=self.book,
            inventory_number="INV-RES-0001",
            location=self.location,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )

    def test_staff_can_create_reservation_via_api(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            "/api/reservations/",
            {"copy": self.copy.id, "reader": self.reader.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Reservation.Status.ACTIVE)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.RESERVED)

    def test_reader_can_cancel_own_reservation(self):
        reservation = create_reservation(copy_id=self.copy.id, reader=self.reader)
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.post(
            f"/api/reservations/{reservation.id}/cancel/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Reservation.Status.CANCELLED)
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, BookCopy.Status.AVAILABLE)

    def test_reader_can_list_own_reservations_via_my_endpoint(self):
        create_reservation(copy_id=self.copy.id, reader=self.reader)

        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get("/api/reservations/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["reader"], self.reader.id)
