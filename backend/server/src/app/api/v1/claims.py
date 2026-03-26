import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...core.exceptions.http_exceptions import NotFoundException
from ...schemas.claim import ClaimRead
from ..dependencies import DBSession, get_current_worker

router = APIRouter(prefix="/claims", tags=["claims"])

CurrentWorker = Annotated[dict[str, Any], Depends(get_current_worker)]


@router.get("", response_model=list[ClaimRead])
async def list_claims(db: DBSession, worker: CurrentWorker) -> list[dict[str, Any]]:
    # Import here to avoid circular imports
    from ...models.claim import Claim

    result = await db.execute(
        select(Claim).where(Claim.worker_id == worker["id"]).order_by(Claim.created_at.desc())
    )
    claims = result.scalars().all()
    return [{c.name: getattr(cl, c.name) for c in Claim.__table__.columns} for cl in claims]


@router.get("/{claim_id}", response_model=ClaimRead)
async def get_claim(claim_id: uuid.UUID, db: DBSession, worker: CurrentWorker) -> dict[str, Any]:
    # Import here to avoid circular imports
    from ...models.claim import Claim

    result = await db.execute(
        select(Claim).where(Claim.id == claim_id, Claim.worker_id == worker["id"])
    )
    claim = result.scalar_one_or_none()
    if claim is None:
        raise NotFoundException("Claim not found.")
    return {c.name: getattr(claim, c.name) for c in Claim.__table__.columns}
