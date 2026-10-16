"""Shared FastAPI dependencies. Every feature router composes these instead of
re-implementing auth/RBAC checks — this is the one place tenant isolation and
role enforcement live, per the "every query is tenant-scoped" rule."""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.enums import OrgRole, role_at_least
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import TokenType, decode_token
from app.features.auth.models import User
from app.features.organizations.models import OrgMembership

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token")

    payload = decode_token(credentials.credentials, TokenType.ACCESS)
    user_id = uuid.UUID(payload["sub"])

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user


class OrgContext:
    """The resolved tenant context for an org-scoped request: which org, which
    user, and their role in it. Route handlers depend on `require_role(...)`
    (below) rather than constructing this directly."""

    def __init__(self, org_id: uuid.UUID, user: User, membership: OrgMembership) -> None:
        self.org_id = org_id
        self.user = user
        self.membership = membership
        self.role = membership.role


def require_role(minimum: OrgRole):
    """Dependency factory: `Depends(require_role(OrgRole.ADMIN))`. Resolves the
    :orgId path param, verifies membership, and enforces the minimum role —
    a user who isn't a member of the org gets 404 (not 403) so membership
    itself isn't leaked to non-members."""

    async def dependency(
        org_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> OrgContext:
        result = await db.execute(
            select(OrgMembership).where(
                OrgMembership.org_id == org_id,
                OrgMembership.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if membership is None:
            raise NotFoundError("Organization not found")

        if not role_at_least(membership.role, minimum):
            raise ForbiddenError(f"Requires at least '{minimum.value}' role in this organization")

        return OrgContext(org_id=org_id, user=current_user, membership=membership)

    return dependency
