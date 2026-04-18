from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, User


class AuthMeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="me-test@example.com",
            password="strong-pass-123",
            first_name="Me",
            last_name="Test",
            role=Role.READER,
        )
        self.reader = Reader.objects.create(
            user=self.user,
            card_number="CARD-ME-001",
            phone_number="+79990000060",
            email="me-reader-profile@example.com",
            address="Me St 1",
        )

    def test_me_requires_auth(self):
        response = self.client.get("/api/auth/me/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_me_reader_returns_reader_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/auth/me/reader/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reader.id)
        self.assertEqual(response.data["card_number"], self.reader.card_number)
