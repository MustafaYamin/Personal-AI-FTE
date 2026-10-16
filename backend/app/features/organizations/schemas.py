import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import OrgRole


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)


class MemberOut(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    full_name: str
    role: OrgRole
    joined_at: datetime


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: OrgRole = OrgRole.MEMBER


class InviteMemberResponse(BaseModel):
    invitation_id: uuid.UUID
    email: EmailStr
    role: OrgRole
    expires_at: datetime
    # Dev-mode only: Phase 5 (Gmail integration) will deliver this by email
    # instead of returning it in the response body.
    invite_token: str


class AcceptInvitationRequest(BaseModel):
    full_name: str | None = Field(default=None, description="Required only if the invited email has no account yet")
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UpdateMemberRoleRequest(BaseModel):
    role: OrgRole
