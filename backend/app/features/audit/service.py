"""record_event() is the ONE place that writes to audit_events. Every other
feature (auth, organizations, and later tasks/approvals) calls this instead of
inserting rows itself — that's what keeps the redaction rule and schema
consistent across the whole app."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ActionType, ApprovalStatus, ActionResult
from app.features.audit.models import AuditEvent

_REDACTED = "***REDACTED***"
_SENSITIVE_KEY_MARKERS = ("password", "token", "secret", "key", "credential", "api_key", "access_token", "refresh_token")


def _sanitize(value: dict) -> dict:
    """Recursively redact any key that looks like it holds a secret. Ported
    verbatim (as a rule set) from the legacy audit_logger.py sanitizer."""

    def _sanitize_value(v):
        if isinstance(v, dict):
            return _sanitize(v)
        if isinstance(v, list):
            return [_sanitize_value(item) for item in v]
        return v

    sanitized = {}
    for k, v in value.items():
        if any(marker in k.lower() for marker in _SENSITIVE_KEY_MARKERS):
            sanitized[k] = _REDACTED
        else:
            sanitized[k] = _sanitize_value(v)
    return sanitized


async def record_event(
    db: AsyncSession,
    *,
    org_id: uuid.UUID,
    action_type: ActionType,
    target: str,
    actor_id: uuid.UUID | None = None,
    actor_type: str = "user",
    parameters: dict | None = None,
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED,
    approved_by_id: uuid.UUID | None = None,
    result: ActionResult = ActionResult.SUCCESS,
    error_message: str | None = None,
    event_metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        org_id=org_id,
        actor_id=actor_id,
        actor_type=actor_type,
        action_type=action_type.value,
        target=target,
        parameters=_sanitize(parameters or {}),
        approval_status=approval_status.value,
        approved_by_id=approved_by_id,
        result=result.value,
        error_message=error_message,
        event_metadata=event_metadata or {},
    )
    db.add(event)
    await db.flush()
    return event
