from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .token_blacklist import TokenBlacklist


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    result = await db.execute(
        select(TokenBlacklist).where(
            TokenBlacklist.token == token,
            TokenBlacklist.expires_at > datetime.now(UTC),
        )
    )
    return result.scalar_one_or_none() is not None


async def create_blacklisted_token(db: AsyncSession, token: str, expires_at: datetime) -> None:
    db.add(TokenBlacklist(token=token, expires_at=expires_at))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
