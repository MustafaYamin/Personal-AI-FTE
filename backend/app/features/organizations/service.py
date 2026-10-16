import secrets
import uuid
from datetime import datetime, timedelta, timezone

from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import ActionType, OrgRole
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import TokenPairData, hash_password, hash_token
from app.features.audit.service import record_event
from app.features.auth.models import User
from app.features.auth.tokens import issue_token_pair
from app.features.organizations.models import Organization, OrgInvitation, OrgMembership

INVITATION_EXPIRE_DAYS = 7


async def _unique_slug(db: AsyncSession, base_name: str) -> str:
    base = slugify(base_name) or "org"
    slug = base
    suffix = 1
    while (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


async def create_organization_for_user(db: AsyncSession, *, owner: User, org_name: str) -> Organization:
    """Shared by signup (new user's first org) and the "create another org"
    endpoint (existing user starting a second org) — the only two ways an
    organization comes into existence, so the slug/membership/audit logic
    lives in exactly one place."""
    slug = await _unique_slug(db, org_name)
    org = Organization(name=org_name, slug=slug)
    db.add(org)
    await db.flush()

    db.add(OrgMembership(org_id=org.id, user_id=owner.id, role=OrgRole.OWNER))
    await db.flush()

    await record_event(
        db,
        org_id=org.id,
        actor_id=owner.id,
        action_type=ActionType.ORG_CREATE,
        target=f"organization:{org.id}",
        parameters={"org_name": org_name},
    )
    return org


async def list_members(db: AsyncSession, org_id: uuid.UUID) -> list[OrgMembership]:
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.org_id == org_id)
        .options(selectinload(OrgMembership.user))
        .order_by(OrgMembership.created_at)
    )
    return result.scalars().all()


async def _count_owners(db: AsyncSession, org_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(OrgMembership).where(
            OrgMembership.org_id == org_id, OrgMembership.role == OrgRole.OWNER
        )
    )
    return result.scalar_one()


async def invite_member(
    db: AsyncSession, *, org_id: uuid.UUID, inviter: User, email: str, role: OrgRole
) -> tuple[OrgInvitation, str]:
    if role == OrgRole.OWNER:
        raise ForbiddenError("Cannot invite someone directly as owner — promote an existing member instead")

    raw_token = secrets.token_urlsafe(32)
    invitation = OrgInvitation(
        org_id=org_id,
        email=email,
        role=role,
        token_hash=hash_token(raw_token),
        invited_by_id=inviter.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=INVITATION_EXPIRE_DAYS),
    )
    db.add(invitation)
    await db.flush()

    await record_event(
        db,
        org_id=org_id,
        actor_id=inviter.id,
        action_type=ActionType.ORG_MEMBER_INVITE,
        target=f"invitation:{invitation.id}",
        parameters={"email": email, "role": role.value},
    )
    await db.commit()
    return invitation, raw_token


async def accept_invitation(
    db: AsyncSession, *, raw_token: str, full_name: str | None, password: str | None
) -> tuple[User, TokenPairData]:
    token_hash = hash_token(raw_token)
    invitation = (
        await db.execute(select(OrgInvitation).where(OrgInvitation.token_hash == token_hash))
    ).scalar_one_or_none()

    if invitation is None:
        raise NotFoundError("Invitation not found")
    if invitation.accepted_at is not None:
        raise ConflictError("Invitation has already been accepted")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise ConflictError("Invitation has expired")

    user = (await db.execute(select(User).where(User.email == invitation.email))).scalar_one_or_none()

    if user is None:
        if not full_name or not password:
            raise ConflictError("full_name and password are required to create an account for this invitation")
        user = User(email=invitation.email, full_name=full_name, hashed_password=hash_password(password))
        db.add(user)
        await db.flush()

    existing_membership = (
        await db.execute(
            select(OrgMembership).where(
                OrgMembership.org_id == invitation.org_id, OrgMembership.user_id == user.id
            )
        )
    ).scalar_one_or_none()

    if existing_membership is None:
        db.add(OrgMembership(org_id=invitation.org_id, user_id=user.id, role=invitation.role))

    invitation.accepted_at = datetime.now(timezone.utc)
    await db.flush()

    await record_event(
        db,
        org_id=invitation.org_id,
        actor_id=user.id,
        action_type=ActionType.ORG_MEMBER_JOIN,
        target=f"user:{user.id}",
        parameters={"role": invitation.role.value},
    )

    tokens = await issue_token_pair(db, user.id)

    await db.commit()
    return user, tokens


async def update_member_role(
    db: AsyncSession, *, org_id: uuid.UUID, actor: User, actor_role: OrgRole, target_user_id: uuid.UUID, new_role: OrgRole
) -> OrgMembership:
    membership = (
        await db.execute(
            select(OrgMembership).where(OrgMembership.org_id == org_id, OrgMembership.user_id == target_user_id)
        )
    ).scalar_one_or_none()
    if membership is None:
        raise NotFoundError("Member not found")

    # Only an owner may grant or revoke owner status — an admin promoting
    # themselves (or anyone) to owner would be a privilege escalation.
    if (new_role == OrgRole.OWNER or membership.role == OrgRole.OWNER) and actor_role != OrgRole.OWNER:
        raise ForbiddenError("Only an owner can change owner-level roles")

    if membership.role == OrgRole.OWNER and new_role != OrgRole.OWNER:
        if await _count_owners(db, org_id) <= 1:
            raise ConflictError("Cannot demote the last owner of an organization")

    old_role = membership.role
    membership.role = new_role
    await db.flush()

    await record_event(
        db,
        org_id=org_id,
        actor_id=actor.id,
        action_type=ActionType.ORG_MEMBER_ROLE_CHANGE,
        target=f"user:{target_user_id}",
        parameters={"old_role": old_role.value, "new_role": new_role.value},
    )
    await db.commit()
    return membership


async def remove_member(db: AsyncSession, *, org_id: uuid.UUID, actor: User, target_user_id: uuid.UUID) -> None:
    membership = (
        await db.execute(
            select(OrgMembership).where(OrgMembership.org_id == org_id, OrgMembership.user_id == target_user_id)
        )
    ).scalar_one_or_none()
    if membership is None:
        raise NotFoundError("Member not found")

    if membership.role == OrgRole.OWNER and await _count_owners(db, org_id) <= 1:
        raise ConflictError("Cannot remove the last owner of an organization")

    await db.delete(membership)
    await record_event(
        db,
        org_id=org_id,
        actor_id=actor.id,
        action_type=ActionType.ORG_MEMBER_REMOVE,
        target=f"user:{target_user_id}",
    )
    await db.commit()
