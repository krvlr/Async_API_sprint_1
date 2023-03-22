from typing import Optional

from redis.asyncio.client import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis
