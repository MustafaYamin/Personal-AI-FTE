import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, UUIDPKMixin


class AuditEvent(Base, UUIDPKMixin, TenantMixin):
    """Append-only. This is the source of truth for "what happened and when" —
    ported from the legacy audit_logger.py AuditEntry shape. Never update or
    delete rows here; if a correction is needed, append a new event.

    Note: the column is `event_metadata`, not `metadata` — SQLAlchemy's
    Declarative base reserves `.metadata` on every mapped class."""

    __tablename__ = "audit_events"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target: Mapped[str] = mapped_column(String(500), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, default="not_required")
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    result: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
