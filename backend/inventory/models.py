from django.db import models


class Location(models.Model):
    name = models.CharField("Название", max_length=100)
    code = models.CharField("Код", max_length=20, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="Родительское место",
    )

    class Meta:
        verbose_name = "Местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def full_path(self):
        parts = [self.name]
        obj = self
        while obj.parent_id:
            obj = obj.parent
            parts.insert(0, obj.name)
        return " / ".join(parts)


class BookCopy(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Доступен"
        ON_LOAN = "on_loan", "На руках"
        RESERVED = "reserved", "Забронирован"
        LOST = "lost", "Утерян"
        REPAIR = "repair", "На ремонте"
        WRITTEN_OFF = "written_off", "Списан"

    book = models.ForeignKey(
        "catalog.Book",
        on_delete=models.PROTECT,
        related_name="copies",
        verbose_name="Книга",
    )
    inventory_number = models.CharField(
        "Инвентарный номер", max_length=50, unique=True, db_index=True
    )
    barcode = models.CharField(
        "Штрих-код", max_length=50, unique=True, null=True, blank=True, db_index=True
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copies",
        verbose_name="Местоположение",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )
    acquired_date = models.DateField("Дата поступления")
    writeoff_date = models.DateField("Дата списания", null=True, blank=True)
    notes = models.TextField("Примечания", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Экземпляр книги"
        verbose_name_plural = "Экземпляры книг"
        ordering = ["inventory_number"]
        indexes = [
            models.Index(fields=["book", "status"]),
        ]

    def __str__(self):
        return f"#{self.inventory_number} «{self.book.title}» [{self.get_status_display()}]"

    # Хелперы — вызываются из circulation и reservations
    def mark_on_loan(self):
        self.status = self.Status.ON_LOAN
        self.save(update_fields=["status", "updated_at"])

    def mark_available(self):
        self.status = self.Status.AVAILABLE
        self.save(update_fields=["status", "updated_at"])

    def mark_reserved(self):
        self.status = self.Status.RESERVED
        self.save(update_fields=["status", "updated_at"])

    def mark_lost(self):
        self.status = self.Status.LOST
        self.save(update_fields=["status", "updated_at"])
