"""Same aggregation pattern as backend/app/api.py — add a new feature's
router here as the agent-loop/reasoning features land in Phase 4+."""

from fastapi import APIRouter

from app.features.health.router import router as health_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
