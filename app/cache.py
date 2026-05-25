from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import redis.asyncio as redis

logger = logging.getLogger("spimex_api.cache")

_cache: RedisCache | None = None # глобал


class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        await self.redis.set(key, value, ex=ex)

    async def flush(self):
        await self.redis.flushdb()
        logger.info("Кэш Redis полностью очищен")

    async def close(self):
        await self.redis.aclose()


def set_cache(cache: RedisCache):
    global _cache
    _cache = cache


def get_cache() -> RedisCache:
    global _cache
    if _cache is None:
        raise RuntimeError("Redis кэш ещё не инициализирован")
    return _cache


async def schedule_flush():
    """Фоновая задача для ежедневного сброса кэша в 14:11."""
    cache = get_cache()
    while True:
        now = datetime.now()
        target = now.replace(hour=14, minute=11, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        logger.info(f"Следующая очистка кэша в {target.isoformat()} (через {wait_seconds:.0f} сек)")
        await asyncio.sleep(wait_seconds)
        try:
            await cache.flush()
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
