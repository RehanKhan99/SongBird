import logging

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.exception(f"DB health check failed: {e}")
        return False


async def check_redis_health(redis: Redis) -> bool:
    try:
        await redis.ping()
        return True
    except Exception as e:
        logger.exception(f"Redis health check failed: {e}")
        return False
