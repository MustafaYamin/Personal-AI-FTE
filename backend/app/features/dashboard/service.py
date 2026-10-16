import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.dashboard.schemas import DashboardSummary


async def get_summary(db: AsyncSession, org_id: uuid.UUID) -> DashboardSummary:
    # Placeholder until Phase 2 introduces tasks/approvals tables to aggregate.
    return DashboardSummary()
