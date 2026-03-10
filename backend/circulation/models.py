from django.conf import settings
from django.db import models


class Loan(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "На руках"
        RETURNED = "returned", "Возвращена"
        OVERDUE = "overdue", "Просрочена"
        LOST = "lost", "Утеряна"

    copy = models.ForeignKey(
        "inventory.BookCopy",
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name="Экземпляр",
    )
    reader = models.ForeignKey(
        "accounts.Reader",
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name="Читатель",
    )
    issued_by = models.ForeignKey(
        "accounts.Staff",
        on_delete=models.PROTECT,
        related_name="issued_loans",
        verbose_name="Выдал",
    )
    issue_date = models.DateField("Дата выдачи", auto_now_add=True)
    due_date = models.DateField("Срок возврата")
    return_date = models.DateField("Дата возврата", null=True, blank=True)
    return_processed_by = models.ForeignKey(
        "accounts.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returned_loans",
        verbose_name="Принял возврат",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    renewals_count = models.PositiveSmallIntegerField("Количество продлений", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Выдача"
        verbose_name_plural = "Выдачи"
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=["reader", "status"]),
            models.Index(fields=["copy", "status"]),
        ]

    def __str__(self):
        return f"Loan #{self.pk} | {self.reader} | {self.copy} | {self.get_status_display()}"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_overdue(self):
        from datetime import date

        return self.status == self.Status.ACTIVE and date.today() > self.due_date
