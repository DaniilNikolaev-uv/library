from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Reader, Role, User
from audit.models import AuditAction, AuditLog
from audit.services import audit_log


class AuditApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email="admin-audit@example.com",
            password="strong-pass-123",
            first_name="Admin",
            last_name="Audit",
            role=Role.ADMIN,
            is_staff=True,
        )
        self.librarian_user = User.objects.create_user(
            email="librarian-audit@example.com",
            password="strong-pass-123",
            first_name="Lib",
            last_name="Audit",
            role=Role.LIBRARIAN,
            is_staff=True,
        )
        self.reader_user = User.objects.create_user(
            email="reader-audit@example.com",
            password="strong-pass-123",
            first_name="Read",
            last_name="Audit",
            role=Role.READER,
        )
        Reader.objects.create(
            user=self.reader_user,
            card_number="CARD-AUD-001",
            phone_number="+79990000050",
            email="reader-audit-profile@example.com",
            address="Audit St 1",
        )
        self.log = AuditLog.objects.create(
            user=self.admin_user,
            entity_type="Loan",
            entity_id="42",
            action=AuditAction.ISSUE,
            data_after={"id": 42},
        )

    def test_admin_can_list_audit_logs(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/audit/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        ids = [row["id"] for row in response.data]
        self.assertIn(self.log.id, ids)

    def test_admin_can_retrieve_audit_log(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/audit/{self.log.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.log.id)
        self.assertEqual(response.data["action"], AuditAction.ISSUE)
        self.assertEqual(response.data["user_email"], self.admin_user.email)
        self.assertEqual(response.data["action_display"], AuditAction.ISSUE.label)

    def test_admin_can_filter_audit_logs(self):
        AuditLog.objects.create(
            user=self.admin_user,
            entity_type="Fine",
            entity_id="9",
            action=AuditAction.PAY_FINE,
            data_after={"id": 9},
        )
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/audit/?action=issue&entity_type=Loan")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.log.id)

    def test_librarian_forbidden_on_audit(self):
        self.client.force_authenticate(user=self.librarian_user)
        response = self.client.get("/api/audit/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reader_forbidden_on_audit(self):
        self.client.force_authenticate(user=self.reader_user)
        response = self.client.get("/api/audit/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_audit_list(self):
        response = self.client.get("/api/audit/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class AuditServiceTests(TestCase):
    def test_audit_log_serializes_entity_when_data_after_is_missing(self):
        user = User.objects.create_user(
            email="service-audit@example.com",
            password="strong-pass-123",
            first_name="Service",
            last_name="Audit",
            role=Role.READER,
        )
        reader = Reader.objects.create(
            user=user,
            card_number="CARD-AUD-SERVICE",
            phone_number="+79990000100",
            email="service-audit-reader@example.com",
            address="Service St 1",
        )

        log = audit_log(user=user, action=AuditAction.UPDATE, entity=reader)

        self.assertEqual(log.entity_type, "Reader")
        self.assertEqual(log.entity_id, str(reader.pk))
        self.assertIsInstance(log.data_after, dict)
        self.assertEqual(log.data_after["user"], user.pk)
        self.assertEqual(log.data_before["card_number"], reader.card_number)
