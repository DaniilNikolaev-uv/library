from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        FULFILLED = "fulfilled", "Выдано"
        CANCELLED = "cancelled", "Отменена"
        EXPIRED = "expired", "Истекла"

    copy = models.ForeignKey(
        "inventory.BookCopy",
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="Экземпляр",
    )
    reader = models.ForeignKey(
        "accounts.Reader",
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="Читатель",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField("Истекает", db_index=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["copy", "status"]),
            models.Index(fields=["reader", "status"]),
        ]

    def __str__(self) -> str:
        return f"Reservation #{self.pk} {self.reader} -> {self.copy} ({self.status})"

    @classmethod
    def default_expires_at(cls):
        hours = int(getattr(settings, "RESERVATION_HOURS", 48))
        return timezone.now() + timedelta(hours=hours)
