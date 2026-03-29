import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse

from ...core.exceptions.http_exceptions import ForbiddenException
from ...core.utils.cache import async_get_redis
from ..dependencies import get_admin_user, get_current_worker

router = APIRouter(prefix="/events", tags=["events"])

# Trigger publishes to these channels
WORKER_CHANNEL = "songbird:worker:{worker_id}"
ADMIN_CHANNEL = "songbird:admin"


async def _subscribe_stream(
    request: Request,
    redis: Redis,
    channel: str,
) -> AsyncGenerator[dict[str, str], None]:
    """Subscribe to a Redis pub/sub channel and yield SSE events until disconnect."""
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            if await request.is_disconnected():
                break
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and isinstance(msg.get("data"), bytes):
                try:
                    payload = json.loads(msg["data"])
                    yield {
                        "event": payload.get("event", "message"),
                        "data": json.dumps(payload),
                    }
                except (json.JSONDecodeError, KeyError):
                    pass
    except asyncio.CancelledError:
        # Handle cleanup here
        raise  # Crucial: Propagate the cancellation
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()


@router.get("/worker/{worker_id}")
async def worker_events(
    worker_id: uuid.UUID,
    request: Request,
    redis: Annotated[Redis, Depends(async_get_redis)],
    worker: Annotated[dict[str, Any], Depends(get_current_worker)],
) -> EventSourceResponse:
    if worker["id"] != worker_id:
        raise ForbiddenException("Cannot subscribe to another worker's stream.")
    channel = WORKER_CHANNEL.format(worker_id=worker_id)
    return EventSourceResponse(_subscribe_stream(request, redis, channel))


@router.get("/admin")
async def admin_events(
    request: Request,
    redis: Annotated[Redis, Depends(async_get_redis)],
    _: Annotated[dict[str, Any], Depends(get_admin_user)],
) -> EventSourceResponse:
    return EventSourceResponse(_subscribe_stream(request, redis, ADMIN_CHANNEL))
