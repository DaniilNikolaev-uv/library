from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "create"
    UPDATE = "update", "update"
    DELETE = "delete", "delete"
    ISSUE = "issue", "issue"
    RETURN = "return", "return"
    RENEW = "renew", "renew"
    RESERVE = "reserve", "reserve"
    CANCEL_RESERVATION = "cancel_reservation", "cancel_reservation"
    PAY_FINE = "pay_fine", "pay_fine"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Пользователь",
    )
    entity_type = models.CharField("Тип сущности", max_length=100, db_index=True)
    entity_id = models.CharField("ID сущности", max_length=64, db_index=True)
    action = models.CharField(
        "Действие", max_length=50, choices=AuditAction.choices, db_index=True
    )
    timestamp = models.DateTimeField("Время", auto_now_add=True, db_index=True)
    data_before = models.JSONField("До", null=True, blank=True)
    data_after = models.JSONField("После", null=True, blank=True)
    meta = models.JSONField("Мета", null=True, blank=True)

    class Meta:
        verbose_name = "Аудит"
        verbose_name_plural = "Аудит"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} {self.action} {self.entity_type}#{self.entity_id}"
