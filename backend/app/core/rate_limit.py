"""Fixed-window rate limiter backed by Redis, so limits hold across every
backend replica once this runs behind a load balancer at 10k-user scale.

Fails OPEN (allows the request but logs) if Redis is unreachable — availability
of auth endpoints matters more than strict limiting during a Redis blip."""

import logging

from fastapi import Depends, Request

from app.core.exceptions import RateLimitedError
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


def rate_limit(times: int, seconds: int, *, key_prefix: str):
    async def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{key_prefix}:{client_ip}"
        redis = get_redis()
        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, seconds)
        except Exception:
            logger.warning("Rate limiter unavailable (Redis down?) — failing open for %s", key)
            return

        if count > times:
            raise RateLimitedError(f"Too many requests — try again in {seconds} seconds")

    return Depends(dependency)
