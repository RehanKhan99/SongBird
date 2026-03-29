import asyncio
import logging
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Literal

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db.crud_token_blacklist import create_blacklisted_token, is_token_blacklisted
from .schemas import TokenData

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


async def get_password_hash(password: str) -> str:
    return await asyncio.to_thread(
        lambda: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )


async def verify_password(plain: str, hashed: str) -> bool:
    # bcrypt is CPU-bound : offload to thread to avoid blocking the event loop
    return await asyncio.to_thread(bcrypt.checkpw, plain.encode(), hashed.encode())


async def authenticate_user(
    db: AsyncSession, username_or_email: str, password: str
) -> dict[str, Any] | Literal[False]:
    # Import here to avoid circular imports
    from ..models.user import User

    if "@" in username_or_email:
        result = await db.execute(
            select(User).where(User.email == username_or_email, User.is_deleted.is_(False))
        )
    else:
        result = await db.execute(
            select(User).where(User.username == username_or_email, User.is_deleted.is_(False))
        )

    user = result.scalar_one_or_none()
    if not user or not await verify_password(password, user.hashed_password):
        return False
    return {c.name: getattr(user, c.name) for c in User.__table__.columns}


def _make_token(data: dict[str, Any], token_type: str, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload.update({
        "exp": datetime.now(UTC).replace(tzinfo=None) + expires_delta,
        "token_type": token_type,
    })
    return str(
        jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
    )


async def create_access_token(data: dict[str, Any]) -> str:
    return _make_token(
        data, TokenType.ACCESS, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


async def create_refresh_token(data: dict[str, Any]) -> str:
    return _make_token(data, TokenType.REFRESH, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


async def verify_token(token: str, expected_type: TokenType, db: AsyncSession) -> TokenData | None:
    if await is_token_blacklisted(db, token):
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM]
        )
        sub: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if sub is None or token_type != expected_type:
            return None
        return TokenData(username_or_email=sub)
    except JWTError:
        return None


async def blacklist_token(token: str, db: AsyncSession) -> None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        if exp:
            await create_blacklisted_token(db, token, datetime.fromtimestamp(exp, tz=UTC))
    except JWTError as e:
        logger.warning("blacklist_token: could not decode token — %s", e)
