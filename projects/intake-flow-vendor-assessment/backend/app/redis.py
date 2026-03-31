import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool


async def close_redis():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
