from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from circulation.models import Loan

from .models import Fine, FinePolicy


@dataclass(frozen=True)
class FineCalcResult:
    overdue_days: int
    amount: Decimal


def get_active_policy() -> FinePolicy | None:
    return FinePolicy.objects.filter(is_active=True).order_by("-created_at").first()


def calculate_fine_for_loan(loan: Loan, policy: FinePolicy) -> FineCalcResult:
    """
    Считает штраф по просрочке. Считаем по дате фактического возврата (если есть),
    иначе по сегодняшней дате.
    """
    end_date: date = loan.return_date or date.today()
    overdue_days = (end_date - loan.due_date).days
    if overdue_days <= 0:
        return FineCalcResult(overdue_days=0, amount=Decimal("0.00"))

    chargeable_days = max(0, overdue_days - int(policy.grace_period_days or 0))
    if chargeable_days <= 0:
        return FineCalcResult(overdue_days=overdue_days, amount=Decimal("0.00"))

    amount = (policy.daily_rate * Decimal(chargeable_days)).quantize(Decimal("0.01"))
    if amount > policy.max_fine_per_loan:
        amount = policy.max_fine_per_loan
    return FineCalcResult(overdue_days=overdue_days, amount=amount)


@transaction.atomic
def create_fine_for_loan(loan: Loan) -> Fine | None:
    """
    Создаёт (или обновляет) штраф для выдачи, если есть просрочка.
    Возвращает Fine или None, если штраф не нужен / нет активной политики.
    """
    policy = get_active_policy()
    if not policy:
        return None

    result = calculate_fine_for_loan(loan, policy=policy)
    if result.amount <= 0:
        return None

    fine, created = Fine.objects.select_for_update().get_or_create(
        loan=loan,
        defaults={"amount": result.amount},
    )

    if not created and fine.status not in (Fine.Status.CANCELLED, Fine.Status.PAID):
        fine.amount = result.amount
        if fine.paid_amount >= fine.amount:
            fine.status = Fine.Status.PAID
            fine.paid_at = fine.paid_at or timezone.now()
        elif fine.paid_amount > 0:
            fine.status = Fine.Status.PARTIALLY_PAID
        else:
            fine.status = Fine.Status.UNPAID
        fine.save(update_fields=["amount", "status", "paid_at", "updated_at"])

    return fine


@transaction.atomic
def pay_fine(fine: Fine, amount: Decimal) -> Fine:
    fine = Fine.objects.select_for_update().get(pk=fine.pk)
    if fine.status == Fine.Status.CANCELLED:
        raise ValueError("Штраф списан и не может быть оплачен.")

    if amount <= 0:
        raise ValueError("Сумма оплаты должна быть > 0.")

    fine.paid_amount = (fine.paid_amount + amount).quantize(Decimal("0.01"))
    if fine.paid_amount >= fine.amount:
        fine.status = Fine.Status.PAID
        fine.paid_amount = fine.amount
        fine.paid_at = timezone.now()
    else:
        fine.status = Fine.Status.PARTIALLY_PAID
        fine.paid_at = fine.paid_at or timezone.now()

    fine.save(update_fields=["paid_amount", "paid_at", "status", "updated_at"])
    return fine

