from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import rate_limit
from app.features.auth import service
from app.features.auth.models import User
from app.features.auth.schemas import (
    CurrentUserOut,
    LoginRequest,
    LogoutRequest,
    MembershipSummary,
    RefreshRequest,
    SignupRequest,
    SignupResponse,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[rate_limit(5, 60, key_prefix="signup")])
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)) -> SignupResponse:
    user, org, tokens = await service.signup(
        db, org_name=body.org_name, full_name=body.full_name, email=body.email, password=body.password
    )
    return SignupResponse(
        tokens=TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token),
        user=UserOut.model_validate(user),
        org_id=org.id,
        org_slug=org.slug,
    )


@router.post("/login", response_model=TokenPair, dependencies=[rate_limit(10, 60, key_prefix="login")])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    _user, tokens = await service.login(db, email=body.email, password=body.password)
    return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/refresh", response_model=TokenPair, dependencies=[rate_limit(20, 60, key_prefix="refresh")])
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    tokens = await service.refresh_tokens(db, refresh_token=body.refresh_token)
    return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.logout(db, refresh_token=body.refresh_token, user=current_user)


@router.get("/me", response_model=CurrentUserOut)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CurrentUserOut:
    memberships = await service.get_memberships(db, current_user)
    return CurrentUserOut(
        user=UserOut.model_validate(current_user),
        memberships=[
            MembershipSummary(
                org_id=m.org_id, org_name=m.organization.name, org_slug=m.organization.slug, role=m.role
            )
            for m in memberships
        ],
    )
