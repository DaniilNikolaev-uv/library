from __future__ import annotations

from typing import Any

from django.db.models import Model
from django.forms.models import model_to_dict

from .models import AuditLog


def _entity_ref(entity) -> tuple[str, str]:
    return entity.__class__.__name__, str(getattr(entity, "pk", ""))


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Model):
        return getattr(value, "pk", str(value))
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    return value


def _snapshot_entity(entity) -> dict[str, Any] | None:
    try:
        return _serialize_value(model_to_dict(entity))
    except Exception:
        return None


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
        data_before = _snapshot_entity(entity)
    if data_after is None:
        data_after = _snapshot_entity(entity)

    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        data_before=data_before,
        data_after=data_after,
        meta=meta,
    )

