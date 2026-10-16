from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """Stub for Phase 1 — always zero. Phase 2 replaces this with real
    SQL aggregation once the tasks/approvals tables exist (see
    orchestrator.py::update_dashboard in the legacy system this replaces)."""

    pending_tasks: int = 0
    awaiting_approval: int = 0
    completed_today: int = 0
