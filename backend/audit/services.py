from __future__ import annotations

from typing import Any

from django.forms.models import model_to_dict

from .models import AuditLog


def _entity_ref(entity) -> tuple[str, str]:
    return entity.__class__.__name__, str(getattr(entity, "pk", ""))


def audit_log(
    *,
    user,
    action: str,
    entity,
    data_before: dict[str, Any] | None = None,
    data_after: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> AuditLog:
    entity_type, entity_id = _entity_ref(entity)

    if data_before is None:
        try:
            data_before = model_to_dict(entity)
        except Exception:
            data_before = None

    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        data_before=data_before,
        data_after=data_after,
        meta=meta,
    )

