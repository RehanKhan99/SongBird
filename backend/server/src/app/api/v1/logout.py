from typing import Annotated

from fastapi import APIRouter, Depends

from ...core.security import blacklist_token, oauth2_scheme
from ..dependencies import DBSession, get_admin_user

router = APIRouter(tags=["auth"])

# logout
@router.post("/logout", status_code=204)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
    _: Annotated[dict, Depends(get_admin_user)],  # ensures token is valid before blacklisting
) -> None:
    await blacklist_token(token, db)
