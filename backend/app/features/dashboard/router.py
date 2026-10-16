import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import OrgContext, require_role
from app.core.enums import OrgRole
from app.features.dashboard import service
from app.features.dashboard.schemas import DashboardSummary

router = APIRouter(prefix="/organizations/{org_id}/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def summary(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _ctx: OrgContext = Depends(require_role(OrgRole.VIEWER)),
) -> DashboardSummary:
    return await service.get_summary(db, org_id)
