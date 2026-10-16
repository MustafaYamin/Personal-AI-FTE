import logging
from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)
