import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...core.constants import TIER_BASE_PREMIUM
from ...core.exceptions.http_exceptions import BadRequestException, NotFoundException
from ...schemas.policy import PolicyAutoRenewToggle, PolicyCreate, PolicyRead, PolicyStatus
from ...schemas.worker import MandateStatus
from ..dependencies import DBSession, get_current_worker

router = APIRouter(prefix="/policies", tags=["policies"])

CurrentWorker = Annotated[dict[str, Any], Depends(get_current_worker)]


@router.get("", response_model=list[PolicyRead])
async def list_policies(db: DBSession, worker: CurrentWorker) -> list[dict[str, Any]]:
    # Import here to avoid circular imports
    from ...models.policy import Policy

    result = await db.execute(
        select(Policy).where(
            Policy.worker_id == worker["id"], Policy.status == PolicyStatus.ACTIVE
        )
    )
    policies = result.scalars().all()
    return [{c.name: getattr(p, c.name) for c in Policy.__table__.columns} for p in policies]


@router.post("", status_code=201, response_model=PolicyRead)
async def create_policy(body: PolicyCreate, db: DBSession, worker: CurrentWorker) -> dict[str, Any]:
    # Import policy from models here
    from ...models.policy import Policy

    tier = body.tier.upper()
    if tier not in TIER_BASE_PREMIUM:
        raise BadRequestException(f"Invalid tier. Choose from: {list(TIER_BASE_PREMIUM)}")

    # one active policy per worker
    existing = await db.execute(
        select(Policy).where(
            Policy.worker_id == worker["id"], Policy.status == PolicyStatus.ACTIVE
        )
    )
    if existing.scalar_one_or_none():
        raise BadRequestException("Worker already has an active policy.")

    # Check for cooling-off period enforcement
    recent_policy_result = await db.execute(
        select(Policy)
        .where(Policy.worker_id == worker["id"])
        .order_by(Policy.created_at.desc())
        .limit(1)
    )
    recent_policy = recent_policy_result.scalar_one_or_none()
    
    if recent_policy and recent_policy.cooling_off_ends_at:
        import datetime
        # If today is before the cooling off ends, block the purchase
        if datetime.datetime.now(datetime.UTC) < recent_policy.cooling_off_ends_at:
            raise BadRequestException(
                "Your cooling-off period is still active. Cannot purchase a new policy."
            )

    base = TIER_BASE_PREMIUM[tier]
    policy = Policy(
        worker_id=worker["id"],
        tier=tier,
        base_premium=base,
        weekly_premium=base,  # M1 engine will update this; stub = base for now
        status=PolicyStatus.ACTIVE,
        auto_renew_enabled=True,  # Mandate established at checkout
        policy_week=1,
    )
    db.add(policy)

    # Establish the UPI Auto-Mandate on checkout success
    from ...models.worker import Worker  # Import here to avoid circular imports
    worker_result = await db.execute(select(Worker).where(Worker.id == worker["id"]))
    worker_db = worker_result.scalar_one()
    
    worker_db.mandate_status = MandateStatus.ACTIVE
    worker_db.auto_renew_tier = tier
    if not worker_db.mandate_id:
        import uuid
        worker_db.mandate_id = f"mock_upi_mandate_{uuid.uuid4()}"

    await db.commit()
    await db.refresh(policy)
    return {c.name: getattr(policy, c.name) for c in Policy.__table__.columns}


@router.get("/{policy_id}", response_model=PolicyRead)
async def get_policy(policy_id: uuid.UUID, db: DBSession, worker: CurrentWorker) -> dict[str, Any]:
    # again
    from ...models.policy import Policy

    result = await db.execute(
        select(Policy).where(Policy.id == policy_id, Policy.worker_id == worker["id"])
    )
    policy = result.scalar_one_or_none()
    if policy is None:
        raise NotFoundException("Policy not found.")
    return {c.name: getattr(policy, c.name) for c in Policy.__table__.columns}


@router.patch("/{policy_id}/auto-renew", response_model=PolicyRead)
async def toggle_auto_renew(
    policy_id: uuid.UUID,
    payload: PolicyAutoRenewToggle,
    db: DBSession,
    worker: CurrentWorker
) -> dict[str, Any]:
    from ...models.policy import Policy
    from ...models.worker import Worker  # Import here to avoid circular imports

    # check active policy of worker
    result = await db.execute(
        select(Policy).where(
            Policy.id == policy_id, 
            Policy.worker_id == worker["id"], 
            Policy.status == PolicyStatus.ACTIVE
        )
    )
    policy = result.scalar_one_or_none()
    if policy is None:
        raise NotFoundException("Active policy not found.")

    # get the worker to map mandate status
    worker_result = await db.execute(select(Worker).where(Worker.id == worker["id"]))
    worker_db = worker_result.scalar_one()

    if payload.auto_renew_enabled:
        policy.auto_renew_enabled = True
        worker_db.mandate_status = MandateStatus.ACTIVE
        worker_db.auto_renew_tier = payload.tier.upper()
        if not worker_db.mandate_id:
            worker_db.mandate_id = f"mock_upi_mandate_{uuid.uuid4()}"
    else:
        # User cancelled Auto-Renew? Current policy alive until expiry
        policy.auto_renew_enabled = False
        worker_db.mandate_status = MandateStatus.INACTIVE
        worker_db.auto_renew_tier = None

    await db.commit()
    await db.refresh(policy)
    return {c.name: getattr(policy, c.name) for c in Policy.__table__.columns}
