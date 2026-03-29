
from redis.asyncio import ConnectionPool, Redis

# Populated at startup by lifespan in setup.py
pool: ConnectionPool | None = None
client: Redis | None = None


async def async_get_redis() -> Redis:
    """FastAPI dependency — returns the global Redis client."""
    if client is None:
        raise RuntimeError("Redis client not initialized — lifespan has not started")
    return client
