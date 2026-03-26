from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...core.constants import TRIGGER_STATUS_ACTIVE
from ...schemas.trigger import TriggerEventRead
from ..dependencies import DBSession, get_admin_user

router = APIRouter(prefix="/triggers", tags=["triggers"])

AdminUser = Annotated[dict[str, Any], Depends(get_admin_user)]


@router.get("/active", response_model=list[TriggerEventRead])
async def get_active_triggers(db: DBSession, _: AdminUser) -> list[dict]:
    # Import trigger events here from models
    from ...models.trigger_event import TriggerEvent

    result = await db.execute(
        select(TriggerEvent).where(TriggerEvent.status == TRIGGER_STATUS_ACTIVE)
    )
    events = result.scalars().all()
    return [{c.name: getattr(e, c.name) for c in TriggerEvent.__table__.columns} for e in events]


@router.get("/history", response_model=list[TriggerEventRead])
async def get_trigger_history(db: DBSession, _: AdminUser) -> list[dict]:
    # Import here to avoid circular imports
    from ...models.trigger_event import TriggerEvent

    result = await db.execute(
        select(TriggerEvent).order_by(TriggerEvent.fired_at.desc())
    )
    events = result.scalars().all()
    return [{c.name: getattr(e, c.name) for c in TriggerEvent.__table__.columns} for e in events]
