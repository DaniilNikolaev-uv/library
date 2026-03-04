from django.db import models


# Create your models here.
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField("Born", null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)


class Book(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    authors = models.ManyToManyField("Author", related_name="books")
    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    categories = models.ManyToManyField("Category", related_name="books", blank=True)
    language = models.CharField(max_length=50, default="ru")
    description = models.TextField(blank=True, default="")
    cover_image = models.ImageField(upload_to="covers/", null=True, blank=True)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.title
