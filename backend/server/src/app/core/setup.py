from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import EnvironmentOption, settings
from .db.database import Base, async_engine
from .logger import _handler  # noqa: F401 — ensures logging is configured on import
from .utils import cache


# @Lifespan 
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # @Startup
    cache.pool = redis.ConnectionPool.from_url(settings.REDIS_URL)
    cache.client = redis.Redis.from_pool(cache.pool)  # type: ignore[arg-type]

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # @Shutdown
    if cache.client:
        await cache.client.aclose()  # type: ignore[union-attr]


# factory


def create_application(router: APIRouter) -> FastAPI:

    kwargs: dict = {}
    if settings.ENVIRONMENT == EnvironmentOption.PRODUCTION:
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        **kwargs,
    )

    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
