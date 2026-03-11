from django.db import models


class FinePolicy(models.Model):
    daily_rate = models.DecimalField("Штраф/день", max_digits=10, decimal_places=2)
    max_fine_per_loan = models.DecimalField(
        "Макс. штраф за выдачу", max_digits=10, decimal_places=2
    )
    grace_period_days = models.PositiveSmallIntegerField(
        "Льготный период (дней)", default=0
    )
    is_active = models.BooleanField("Активная", default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Политика штрафов"
        verbose_name_plural = "Политики штрафов"
        ordering = ["-is_active", "-created_at"]

    def __str__(self) -> str:
        return f"{self.daily_rate}/day, max {self.max_fine_per_loan}, grace {self.grace_period_days}d"


class Fine(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Не оплачен"
        PARTIALLY_PAID = "partially_paid", "Частично оплачен"
        PAID = "paid", "Оплачен"
        CANCELLED = "cancelled", "Списан"

    loan = models.OneToOneField(
        "circulation.Loan",
        on_delete=models.PROTECT,
        related_name="fine",
        verbose_name="Выдача",
    )
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    calculated_at = models.DateTimeField("Рассчитан", auto_now_add=True)
    paid_amount = models.DecimalField(
        "Оплачено", max_digits=10, decimal_places=2, default=0
    )
    paid_at = models.DateTimeField("Дата оплаты", null=True, blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Штраф"
        verbose_name_plural = "Штрафы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Fine #{self.pk} for Loan #{self.loan_id}: {self.amount} ({self.status})"
