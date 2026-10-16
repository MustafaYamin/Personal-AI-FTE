import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import OrgContext, get_current_user, require_role
from app.core.enums import OrgRole
from app.features.auth.models import User
from app.features.auth.schemas import TokenPair, UserOut
from app.features.organizations import service
from app.features.organizations.schemas import (
    AcceptInvitationRequest,
    CreateOrganizationRequest,
    InviteMemberRequest,
    InviteMemberResponse,
    MemberOut,
    OrganizationOut,
    UpdateMemberRoleRequest,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: CreateOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationOut:
    """A logged-in user starting a second org — first-org creation happens as
    part of /auth/signup instead, via the same service.create_organization_for_user."""
    org = await service.create_organization_for_user(db, owner=current_user, org_name=body.name)
    await db.commit()
    return OrganizationOut.model_validate(org)


@router.get("/{org_id}/members", response_model=list[MemberOut])
async def list_members(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ctx: OrgContext = Depends(require_role(OrgRole.VIEWER)),
) -> list[MemberOut]:
    memberships = await service.list_members(db, org_id)
    return [
        MemberOut(user_id=m.user_id, email=m.user.email, full_name=m.user.full_name, role=m.role, joined_at=m.created_at)
        for m in memberships
    ]


@router.post("/{org_id}/invitations", response_model=InviteMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: uuid.UUID,
    body: InviteMemberRequest,
    db: AsyncSession = Depends(get_db),
    ctx: OrgContext = Depends(require_role(OrgRole.ADMIN)),
) -> InviteMemberResponse:
    invitation, raw_token = await service.invite_member(
        db, org_id=org_id, inviter=ctx.user, email=body.email, role=body.role
    )
    return InviteMemberResponse(
        invitation_id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        invite_token=raw_token,
    )


@router.patch("/{org_id}/members/{user_id}", response_model=MemberOut)
async def update_member_role(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    body: UpdateMemberRoleRequest,
    db: AsyncSession = Depends(get_db),
    ctx: OrgContext = Depends(require_role(OrgRole.ADMIN)),
) -> MemberOut:
    membership = await service.update_member_role(
        db, org_id=org_id, actor=ctx.user, actor_role=ctx.role, target_user_id=user_id, new_role=body.role
    )
    await db.refresh(membership, attribute_names=["user"])
    return MemberOut(
        user_id=membership.user_id,
        email=membership.user.email,
        full_name=membership.user.full_name,
        role=membership.role,
        joined_at=membership.created_at,
    )


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: OrgContext = Depends(require_role(OrgRole.ADMIN)),
) -> None:
    await service.remove_member(db, org_id=org_id, actor=ctx.user, target_user_id=user_id)


# Invitation acceptance is not org-scoped by path (the token itself carries
# the org), so it lives at /invitations rather than under /organizations/{org_id}.
invitations_router = APIRouter(prefix="/invitations", tags=["organizations"])


@invitations_router.post("/{token}/accept", response_model=TokenPair)
async def accept_invitation(
    token: str,
    body: AcceptInvitationRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    _user, tokens = await service.accept_invitation(
        db, raw_token=token, full_name=body.full_name, password=body.password
    )
    return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)
