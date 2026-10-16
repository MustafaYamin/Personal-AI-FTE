"""Single place that assembles every feature's router. main.py mounts just
this one aggregate router under /api/v1 — adding a new feature means adding
one line here, not touching main.py."""

from fastapi import APIRouter

from app.features.audit.router import router as audit_router
from app.features.auth.router import router as auth_router
from app.features.dashboard.router import router as dashboard_router
from app.features.organizations.router import invitations_router, router as organizations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(invitations_router)
api_router.include_router(audit_router)
api_router.include_router(dashboard_router)
