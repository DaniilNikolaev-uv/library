from pyexpat import model

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.query_utils import PathInfo


class Role(models.TextChoices):
    ADMIN = "admin", "Администратор"
    LIBRARIAN = "librarian", "Библиотекарь"
    READER = "reader", "Читатель"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.READER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]


class Reader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.IntegerField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=200)
    date_registered = models.DateField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LIBRARIAN)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
