from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db.database import async_get_db
from ..core.exceptions.http_exceptions import ForbiddenException, UnauthorizedException
from ..core.security import TokenType, oauth2_scheme, verify_token

# db session
DBSession = Annotated[AsyncSession, Depends(async_get_db)]

# auth: admin

async def get_admin_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> dict[str, Any]:
    """Validates admin JWT. All admin endpoints use this dependency."""
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException("Not authenticated.")

    # Import here to avoid circular imports
    from ..models.user import User

    if "@" in token_data.username_or_email:
        result = await db.execute(
            select(User).where(
                User.email == token_data.username_or_email, User.is_deleted.is_(False)
            )
        )
    else:
        result = await db.execute(
            select(User).where(
                User.username == token_data.username_or_email, User.is_deleted.is_(False)
            )
        )

    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException("Not authenticated.")
    if not user.is_superuser:
        raise ForbiddenException("Admin access required.")

    return {c.name: getattr(user, c.name) for c in User.__table__.columns}


# auth: worker

async def get_current_worker(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> dict[str, Any]:
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException("Not authenticated.")

    # again
    from ..models.worker import Worker

    result = await db.execute(
        select(Worker).where(Worker.phone_number == token_data.username_or_email)
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise UnauthorizedException("Not authenticated.")

    return {c.name: getattr(worker, c.name) for c in Worker.__table__.columns}
