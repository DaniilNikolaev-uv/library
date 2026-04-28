from django.test import TestCase
from unittest.mock import PropertyMock, patch
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role, User
from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url
from catalog.models import Author, Book, Publisher
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

    @patch("django.db.models.fields.files.FieldFile.url", new_callable=PropertyMock)
    def test_book_serializer_ignores_cover_image_storage_errors(self, mocked_url):
        mocked_url.side_effect = RuntimeError("storage unavailable")
        book = Book.objects.create(
            title="Broken Storage Book",
            publisher=self.publisher,
            isbn="978-5-17-118366-6",
            year=2024,
            language="ru",
            description="desc",
        )
        book.authors.add(self.author)
        book.cover_image = "covers/test.jpg"

        data = BookSerializer(instance=book).data

        self.assertIsNone(data["cover_image"])


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(first_name="Alex", last_name="Author")
        self.publisher = Publisher.objects.create(name="Catalog Publisher")
        self.public_book = Book.objects.create(
            title="Public Django Book",
            subtitle="Backend Handbook",
            publisher=self.publisher,
            isbn="978-5-17-118366-6",
            year=2024,
            language="ru",
            description="desc",
        )
        self.public_book.authors.add(self.author)
        self.admin_user = User.objects.create_user(
            email="catalog-admin@example.com",
            password="strong-pass-123",
            first_name="Catalog",
            last_name="Admin",
            role=Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

    def test_anonymous_user_can_list_books(self):
        response = self.client.get("/api/catalog/books/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], self.public_book.title)

    def test_anonymous_user_can_search_books(self):
        response = self.client.get("/api/catalog/books/?search=Django")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.public_book.id)

    def test_anonymous_user_can_list_categories(self):
        response = self.client.get("/api/catalog/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_book(self):
        response = self.client.post(
            "/api/catalog/books/",
            {
                "title": "Forbidden Book",
                "author_ids": [self.author.id],
                "publisher": self.publisher.id,
                "year": 2024,
                "language": "ru",
                "description": "desc",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
