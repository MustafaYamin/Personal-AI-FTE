import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import OrgRole


class SignupRequest(BaseModel):
    org_name: str = Field(min_length=2, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool


class MembershipSummary(BaseModel):
    org_id: uuid.UUID
    org_name: str
    org_slug: str
    role: OrgRole


class CurrentUserOut(BaseModel):
    user: UserOut
    memberships: list[MembershipSummary]


class SignupResponse(BaseModel):
    tokens: TokenPair
    user: UserOut
    org_id: uuid.UUID
    org_slug: str
