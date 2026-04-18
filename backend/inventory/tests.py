from datetime import date

from django.test import TestCase

from catalog.models import Author, Book, Publisher
from inventory.models import BookCopy, Location


class BookCopyModelTests(TestCase):
    def test_str_includes_inventory_and_status(self):
        author = Author.objects.create(first_name="Inv", last_name="Test")
        publisher = Publisher.objects.create(name="Inv Pub")
        book = Book.objects.create(
            title="Inventory Book",
            publisher=publisher,
            isbn="9780000000999",
            year=2021,
            language="ru",
            description="x",
        )
        book.authors.add(author)
        loc = Location.objects.create(name="Shelf", code="INV-T1")
        copy = BookCopy.objects.create(
            book=book,
            inventory_number="INV-TEST-001",
            location=loc,
            status=BookCopy.Status.AVAILABLE,
            acquired_date=date.today(),
        )
        text = str(copy)
        self.assertIn("INV-TEST-001", text)
        self.assertIn("Inventory Book", text)
