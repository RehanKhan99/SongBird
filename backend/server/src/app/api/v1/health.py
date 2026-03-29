from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from ...core.health import check_database_health, check_redis_health
from ...core.utils.cache import async_get_redis
from ..dependencies import DBSession

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(
    db: DBSession,
    redis: Annotated[Redis, Depends(async_get_redis)],
) -> dict:
    db_ok = await check_database_health(db)
    redis_ok = await check_redis_health(redis)
    status = "ok" if db_ok and redis_ok else "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}
