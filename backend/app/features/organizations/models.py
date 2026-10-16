import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import OrgRole
from app.models.base import Base, TenantMixin, TimestampMixin, UUIDPKMixin

_org_role_enum = Enum(OrgRole, name="org_role", values_callable=lambda e: [m.value for m in e])


class Organization(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    memberships: Mapped[list["OrgMembership"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class OrgMembership(Base, UUIDPKMixin, TimestampMixin, TenantMixin):
    __tablename__ = "org_memberships"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_org_memberships_org_user"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[OrgRole] = mapped_column(_org_role_enum, nullable=False, default=OrgRole.MEMBER)

    organization: Mapped["Organization"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")  # noqa: F821


class OrgInvitation(Base, UUIDPKMixin, TimestampMixin, TenantMixin):
    """Invite tokens are stored hashed (like refresh tokens) — the raw token is
    only ever returned once, in the create-invitation response."""

    __tablename__ = "org_invitations"

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    role: Mapped[OrgRole] = mapped_column(_org_role_enum, nullable=False, default=OrgRole.MEMBER)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    invited_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
