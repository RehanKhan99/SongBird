import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...core.security import get_password_hash
from ...schemas.user import UserCreate, UserRead, UserUpdate
from ..dependencies import DBSession, get_admin_user

router = APIRouter(prefix="/users", tags=["users"])

AdminUser = Annotated[dict[str, Any], Depends(get_admin_user)]

# me: i am god
@router.get("/me", response_model=UserRead)
async def get_me(current_user: AdminUser) -> dict[str, Any]:
    return current_user


@router.get("", response_model=list[UserRead])
async def list_users(db: DBSession, _: AdminUser) -> list[dict[str, Any]]:
    # Import here to avoid circular imports
    from ...models.user import User

    result = await db.execute(select(User).where(User.is_deleted.is_(False)))
    users = result.scalars().all()
    return [{c.name: getattr(u, c.name) for c in User.__table__.columns} for u in users]


@router.post("", status_code=201, response_model=UserRead)
async def create_user(body: UserCreate, db: DBSession, _: AdminUser) -> dict[str, Any]:
    # AGAIN
    from ...models.user import User

    exists = await db.execute(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )
    if exists.scalar_one_or_none():
        raise DuplicateValueException("Username or email already exists.")

    user = User(
        name=body.name,
        username=body.username,
        email=body.email,
        hashed_password=await get_password_hash(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {c.name: getattr(user, c.name) for c in User.__table__.columns}


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID, body: UserUpdate, db: DBSession, _: AdminUser
) -> dict[str, Any]:
    # Import here to avoid circular imports
    from ...models.user import User

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted.is_(False))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("User not found.")

    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        user.email = body.email
    if body.password is not None:
        user.hashed_password = await get_password_hash(body.password)

    await db.commit()
    await db.refresh(user)
    return {c.name: getattr(user, c.name) for c in User.__table__.columns}
