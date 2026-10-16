import logging

from fastapi import FastAPI

from app.api import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.debug)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="AI Employee — Reasoning Middleware", version="0.1.0", debug=settings.debug)

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok", "service": "middleware"}

    return app


app = create_app()
