from __future__ import annotations

import logging
from datetime import datetime, timedelta

import redis.asyncio as redis

logger = logging.getLogger("spimex_api.cache")


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        await self.redis.set(key, value, ex=ex)

    async def close(self):
        await self.redis.aclose()


def get_ttl_to_target(hour: int = 14, minute: int = 11) -> int:
    """Возвращает количество секунд до ближайшего указанного времени."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now > target:
        target += timedelta(days=1)
    return int((target - now).total_seconds())