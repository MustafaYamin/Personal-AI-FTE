"""Auth business logic. Routers stay thin — they parse the request, call one
of these, and shape the response."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import ActionType
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import TokenPairData, TokenType, decode_token, hash_password, hash_token, verify_password
from app.features.audit.service import record_event
from app.features.auth.models import RefreshToken, User
from app.features.auth.tokens import issue_token_pair
from app.features.organizations.models import Organization, OrgMembership
from app.features.organizations.service import create_organization_for_user


async def signup(
    db: AsyncSession, *, org_name: str, full_name: str, email: str, password: str
) -> tuple[User, Organization, TokenPairData]:
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is not None:
        raise ConflictError("An account with this email already exists")

    user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
    db.add(user)
    await db.flush()

    org = await create_organization_for_user(db, owner=user, org_name=org_name)

    await record_event(
        db,
        org_id=org.id,
        actor_id=user.id,
        action_type=ActionType.USER_SIGNUP,
        target=f"user:{user.id}",
        parameters={"email": email},
    )

    tokens = await issue_token_pair(db, user.id)
    await db.commit()
    return user, org, tokens


async def login(db: AsyncSession, *, email: str, password: str) -> tuple[User, TokenPairData]:
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")

    tokens = await issue_token_pair(db, user.id)

    # Login events aren't org-scoped yet at this point in the flow, so we log
    # once per membership the user has — keeps every org's audit trail complete.
    memberships = (await db.execute(select(OrgMembership).where(OrgMembership.user_id == user.id))).scalars().all()
    for m in memberships:
        await record_event(
            db,
            org_id=m.org_id,
            actor_id=user.id,
            action_type=ActionType.USER_LOGIN,
            target=f"user:{user.id}",
        )

    await db.commit()
    return user, tokens


async def refresh_tokens(db: AsyncSession, *, refresh_token: str) -> TokenPairData:
    payload = decode_token(refresh_token, TokenType.REFRESH)
    user_id = uuid.UUID(payload["sub"])
    token_hash = hash_token(refresh_token)

    stored = (
        await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    ).scalar_one_or_none()

    if stored is None or stored.revoked_at is not None or stored.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedError("Refresh token is invalid or has been revoked")

    # Rotate: revoke the used token and issue a fresh pair. If a revoked
    # token is ever replayed, this is the point a stolen-token detector
    # would hook in (Phase 9 observability).
    stored.revoked_at = datetime.now(timezone.utc)
    await db.flush()

    tokens = await issue_token_pair(db, user_id)
    await db.commit()
    return tokens


async def logout(db: AsyncSession, *, refresh_token: str, user: User) -> None:
    token_hash = hash_token(refresh_token)
    stored = (
        await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    ).scalar_one_or_none()

    if stored is not None and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        await db.flush()

    memberships = (await db.execute(select(OrgMembership).where(OrgMembership.user_id == user.id))).scalars().all()
    for m in memberships:
        await record_event(
            db, org_id=m.org_id, actor_id=user.id, action_type=ActionType.USER_LOGOUT, target=f"user:{user.id}"
        )

    await db.commit()


async def get_memberships(db: AsyncSession, user: User) -> list[OrgMembership]:
    # Eager-load `organization` — the async ORM has no implicit lazy loading,
    # so callers that read `.organization.name` need it loaded up front.
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.user_id == user.id)
        .options(selectinload(OrgMembership.organization))
    )
    return result.scalars().all()
