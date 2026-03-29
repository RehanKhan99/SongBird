from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...core.security import authenticate_user, create_access_token
from ..dependencies import DBSession

router = APIRouter(tags=["auth"])

# login
@router.post("/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> Token:
    user = await authenticate_user(db, form.username, form.password)
    if not user:
        raise UnauthorizedException("Invalid credentials.")
    payload = {"sub": user["username"]}
    return Token(
        access_token=await create_access_token(payload),
        token_type="bearer",
    )
