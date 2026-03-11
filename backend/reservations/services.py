from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from accounts.models import Reader, Role
from inventory.models import BookCopy

from .models import Reservation


class ReservationError(Exception):
    pass


@transaction.atomic
def create_reservation(*, copy_id: int, reader: Reader) -> Reservation:
    copy = BookCopy.objects.select_for_update().get(pk=copy_id)

    if reader.is_blocked:
        raise ReservationError("Читатель заблокирован.")

    # Разрешаем бронь только на доступный экземпляр (MVP).
    if copy.status != BookCopy.Status.AVAILABLE:
        raise ReservationError(f"Экземпляр недоступен (статус: {copy.get_status_display()}).")

    exists = Reservation.objects.filter(
        copy=copy, reader=reader, status=Reservation.Status.ACTIVE
    ).exists()
    if exists:
        raise ReservationError("У вас уже есть активная бронь на этот экземпляр.")

    reservation = Reservation.objects.create(
        copy=copy,
        reader=reader,
        expires_at=Reservation.default_expires_at(),
        status=Reservation.Status.ACTIVE,
    )
    copy.mark_reserved()
    return reservation


@transaction.atomic
def cancel_reservation(*, reservation_id: int, cancelled_by_user) -> Reservation:
    reservation = (
        Reservation.objects.select_for_update()
        .select_related("copy")
        .get(pk=reservation_id)
    )

    if reservation.status != Reservation.Status.ACTIVE:
        raise ReservationError("Отменить можно только активную бронь.")

    # Разрешаем отмену сотруднику или владельцу
    if getattr(cancelled_by_user, "role", None) == Role.READER:
        try:
            if reservation.reader.user_id != cancelled_by_user.pk:
                raise ReservationError("Нет доступа к этой брони.")
        except Exception:
            raise ReservationError("Нет доступа к этой брони.")

    reservation.status = Reservation.Status.CANCELLED
    reservation.save(update_fields=["status"])

    # Возвращаем экземпляр в available, если он всё ещё зарезервирован именно бронями
    reservation.copy.mark_available()
    return reservation


def expire_reservations() -> int:
    now = timezone.now()
    qs = Reservation.objects.filter(status=Reservation.Status.ACTIVE, expires_at__lt=now)
    count = qs.count()
    # В MVP просто помечаем истёкшими. Статусы копий можно синхронизировать отдельной задачей.
    qs.update(status=Reservation.Status.EXPIRED)
    return count

