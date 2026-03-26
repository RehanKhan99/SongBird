from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from ...core.constants import POLICY_STATUS_ACTIVE, TRIGGER_STATUS_ACTIVE
from ...schemas.admin import DashboardStats
from ...schemas.claim import ClaimRead
from ..dependencies import DBSession, get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[dict[str, Any], Depends(get_admin_user)]


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: DBSession, _: AdminUser) -> DashboardStats:
    # Import here to avoid circular imports
    from ...models.claim import Claim
    from ...models.policy import Policy
    from ...models.trigger_event import TriggerEvent
    from ...models.worker import Worker

    total_workers = (await db.execute(select(func.count()).select_from(Worker))).scalar_one()
    active_policies = (
        await db.execute(
            select(func.count()).select_from(Policy).where(Policy.status == POLICY_STATUS_ACTIVE)
        )
    ).scalar_one()
    active_triggers = (
        await db.execute(
            select(func.count()).select_from(TriggerEvent).where(
                TriggerEvent.status == TRIGGER_STATUS_ACTIVE
            )
        )
    ).scalar_one()
    pending_review = (
        await db.execute(
            select(func.count()).select_from(Claim).where(
                Claim.decision.in_(["CONDITIONAL", "HOLD"])
            )
        )
    ).scalar_one()

    return DashboardStats(
        total_workers=total_workers,
        active_policies=active_policies,
        active_triggers=active_triggers,
        pending_review_claims=pending_review,
    )


@router.get("/claims/review", response_model=list[ClaimRead])
async def get_claims_for_review(db: DBSession, _: AdminUser) -> list[dict[str, Any]]:
    # Import here to avoid circular imports
    from ...models.claim import Claim

    result = await db.execute(
        select(Claim)
        .where(Claim.decision.in_(["CONDITIONAL", "HOLD"]))
        .order_by(Claim.created_at.asc())
    )
    claims = result.scalars().all()
    return [{c.name: getattr(cl, c.name) for c in Claim.__table__.columns} for cl in claims]
