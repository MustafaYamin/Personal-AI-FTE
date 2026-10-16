"""Token issuance that touches the DB (persisting the refresh token). Split out
from service.py so organizations/service.py (invitation acceptance logs a user
in) can reuse it without importing auth/service.py and creating a cycle
(auth.service already needs to call into organizations.service to create the
org on signup)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenPairData, create_access_token, create_refresh_token, hash_token
from app.features.auth.models import RefreshToken


async def issue_token_pair(db: AsyncSession, user_id: uuid.UUID) -> TokenPairData:
    access = create_access_token(user_id)
    refresh, _jti, expires_at = create_refresh_token(user_id)

    db.add(RefreshToken(user_id=user_id, token_hash=hash_token(refresh), expires_at=expires_at))
    await db.flush()

    return TokenPairData(access_token=access, refresh_token=refresh)
