"""
Бизнес-логика circulation.
Все операции выполняются в транзакции.
"""

from datetime import date, timedelta

from django.conf import settings
from django.db import transaction

from accounts.models import Reader, Staff
from inventory.models import BookCopy

from .models import Loan

# Настройки — можно вынести в settings.py
LOAN_DAYS = getattr(settings, "LOAN_DAYS", 14)  # срок выдачи по умолчанию
MAX_ACTIVE_LOANS = getattr(settings, "MAX_ACTIVE_LOANS", 5)  # лимит активных выдач
MAX_RENEWALS = getattr(settings, "MAX_RENEWALS", 2)  # макс. продлений


class LoanError(Exception):
    """Бизнес-ошибка при операциях с выдачей."""

    pass


@transaction.atomic
def issue_book(
    copy_id: int, reader_id: int, staff: Staff, loan_days: int = LOAN_DAYS
) -> Loan:
    """
    Выдать экземпляр читателю.
    Проверки:
      - экземпляр доступен (available)
      - читатель не заблокирован
      - не превышен лимит активных выдач
    """
    copy = BookCopy.objects.select_for_update().get(pk=copy_id)
    reader = Reader.objects.select_for_update().get(pk=reader_id)

    if reader.is_blocked:
        raise LoanError("Читатель заблокирован.")

    if copy.status != BookCopy.Status.AVAILABLE:
        raise LoanError(f"Экземпляр недоступен (статус: {copy.get_status_display()}).")

    active_count = Loan.objects.filter(reader=reader, status=Loan.Status.ACTIVE).count()
    if active_count >= MAX_ACTIVE_LOANS:
        raise LoanError(
            f"У читателя уже {active_count} активных выдач (лимит: {MAX_ACTIVE_LOANS})."
        )

    loan = Loan.objects.create(
        copy=copy,
        reader=reader,
        issued_by=staff,
        due_date=date.today() + timedelta(days=loan_days),
        status=Loan.Status.ACTIVE,
    )
    copy.mark_on_loan()
    _try_audit(staff.user, action="issue", entity=loan)
    return loan


@transaction.atomic
def return_book(loan_id: int, staff: Staff, mark_lost: bool = False) -> Loan:
    """
    Принять возврат.
    Если mark_lost=True — книга помечается как утерянная.
    """
    loan = Loan.objects.select_for_update().select_related("copy").get(pk=loan_id)

    if loan.status not in (Loan.Status.ACTIVE, Loan.Status.OVERDUE):
        raise LoanError(
            f"Нельзя вернуть выдачу со статусом «{loan.get_status_display()}»."
        )

    loan.return_date = date.today()
    loan.return_processed_by = staff

    if mark_lost:
        loan.status = Loan.Status.LOST
        loan.copy.mark_lost()
    else:
        loan.status = Loan.Status.RETURNED
        loan.copy.mark_available()

    loan.save(
        update_fields=["return_date", "return_processed_by", "status", "updated_at"]
    )

    # Создаём штраф если просрочка (если модуль fines подключён)
    _try_create_fine(loan)
    _try_audit(staff.user, action="return", entity=loan)

    return loan


@transaction.atomic
def renew_loan(loan_id: int, staff_or_reader, loan_days: int = LOAN_DAYS) -> Loan:
    """
    Продлить выдачу.
    Проверки:
      - выдача активна
      - не превышен лимит продлений
      - нет активной брони другим читателем на этот экземпляр
    """
    loan = (
        Loan.objects.select_for_update()
        .select_related("copy", "reader")
        .get(pk=loan_id)
    )

    if not loan.is_active:
        raise LoanError("Продлить можно только активную выдачу.")

    if loan.renewals_count >= MAX_RENEWALS:
        raise LoanError(f"Достигнут лимит продлений ({MAX_RENEWALS}).")

    # Проверка наличия активной брони на этот экземпляр другим читателем
    has_reservation = _copy_has_active_reservation(
        loan.copy_id, exclude_reader=loan.reader_id
    )
    if has_reservation:
        raise LoanError("На этот экземпляр есть активная бронь другого читателя.")

    loan.due_date = date.today() + timedelta(days=loan_days)
    loan.renewals_count += 1
    loan.save(update_fields=["due_date", "renewals_count", "updated_at"])
    _try_audit(getattr(staff_or_reader, "user", staff_or_reader), action="renew", entity=loan)
    return loan


def sync_overdue_loans():
    """
    Переводит просроченные активные выдачи в статус overdue.
    Вызывается из management command или celery beat.
    """
    updated = Loan.objects.filter(
        status=Loan.Status.ACTIVE, due_date__lt=date.today()
    ).update(status=Loan.Status.OVERDUE)
    return updated


# ── Вспомогательные ────────────────────────────────────────────────────────


def _copy_has_active_reservation(copy_id: int, exclude_reader_id: int) -> bool:
    try:
        from reservations.models import Reservation

        return (
            Reservation.objects.filter(
                copy_id=copy_id,
                status="active",
            )
            .exclude(reader_id=exclude_reader_id)
            .exists()
        )
    except Exception:
        return False


def _try_create_fine(loan: Loan) -> None:
    """Создаём штраф если просрочка. Тихо падает если fines ещё не подключён."""
    try:
        from fines.services import create_fine_for_loan

        create_fine_for_loan(loan)
    except Exception:
        pass


def _try_audit(user, *, action: str, entity) -> None:
    try:
        from audit.services import audit_log

        audit_log(user=user, action=action, entity=entity, data_after={"id": entity.pk})
    except Exception:
        pass
