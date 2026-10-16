import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id_and_timing(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = request_id
        response.headers["server-timing"] = f"total;dur={duration_ms:.1f}"
        if duration_ms > 500:
            logger.warning(
                "Slow request: %s %s took %.1fms [%s]",
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
        return response
