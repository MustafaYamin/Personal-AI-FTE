from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import require_role
from app.core.enums import OrgRole
from app.core.pagination import Page, PageParams, page_params, paginate
from app.features.audit.models import AuditEvent
from app.features.audit.schemas import AuditEventOut

router = APIRouter(prefix="/organizations/{org_id}/audit-events", tags=["audit"])


@router.get("", response_model=Page[AuditEventOut])
async def list_audit_events(
    org_id,
    params: PageParams = Depends(page_params),
    db: AsyncSession = Depends(get_db),
    _ctx=Depends(require_role(OrgRole.ADMIN)),
) -> Page:
    stmt = select(AuditEvent).where(AuditEvent.org_id == org_id).order_by(AuditEvent.created_at.desc())
    return await paginate(db, stmt, params, AuditEventOut)
