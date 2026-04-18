from django.test import TestCase
from unittest.mock import patch

from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url
from catalog.models import Author, Publisher
from catalog.serializers import BookSerializer


class BookCoverTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="Alex", last_name="Author")
        self.publisher = Publisher.objects.create(name="Test Publisher")

    def test_get_cover_url_uses_isbn(self):
        url = get_cover_url("978-5-17-118366-6")
        self.assertEqual(url, "https://covers.openlibrary.org/b/isbn/9785171183666-M.jpg")

    def test_book_serializer_sets_placeholder_without_isbn(self):
        serializer = BookSerializer(
            data={
                "title": "Test Book",
                "author_ids": [self.author.id],
                "year": 2024,
                "language": "ru",
                "description": "desc",
                "publisher": self.publisher.id,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.cover_url, PLACEHOLDER_COVER_URL)

    def test_book_serializer_sets_cover_url_with_isbn(self):
        serializer = BookSerializer(
            data={
                "title": "ISBN Book",
                "author_ids": [self.author.id],
                "isbn": "978-5-17-118366-6",
                "year": 2024,
                "language": "ru",
                "description": "desc",
                "publisher": self.publisher.id,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.cover_url, "https://covers.openlibrary.org/b/isbn/9785171183666-M.jpg")

    @patch("catalog.serializers.lookup_isbn", return_value="9785171183666")
    def test_book_serializer_autofills_isbn_when_missing(self, mocked_lookup):
        serializer = BookSerializer(
            data={
                "title": "Auto ISBN Book",
                "author_ids": [self.author.id],
                "year": 2024,
                "language": "ru",
                "description": "desc",
                "publisher": self.publisher.id,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()
        self.assertEqual(book.isbn, "9785171183666")
        self.assertEqual(book.cover_url, "https://covers.openlibrary.org/b/isbn/9785171183666-M.jpg")
        mocked_lookup.assert_called_once()
