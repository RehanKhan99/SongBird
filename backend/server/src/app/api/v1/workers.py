import hashlib
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...core.config import settings
from ...core.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    UnauthorizedException,
)
from ...core.schemas import Token
from ...core.security import blacklist_token, create_access_token, oauth2_scheme
from ...schemas.worker import (
    KycStatus,
    MandateStatus,
    WorkerLoginRequest,
    WorkerRead,
    WorkerRegister,
)
from ..dependencies import DBSession, get_current_worker

router = APIRouter(prefix="/workers", tags=["workers"]) 


@router.post("/register", status_code=201, response_model=WorkerRead)
async def register_worker(
    body: WorkerRegister, 
    db: DBSession,
    # platform_client: PlatformClientDependency,
) -> dict[str, Any]:
    # Import here to avoid circular imports
    from ...models.worker import Worker
    # BFM baseline import goes here when model is ready

    exists = await db.execute(
        select(Worker).where(
            (Worker.phone_number == body.phone_number) | (Worker.platform_id == body.platform_id)
        )
    )
    if exists.scalar_one_or_none():
        raise DuplicateValueException("Phone number or platform ID already registered.")

    aadhaar_hash = hashlib.sha256(body.aadhaar_last4.encode()).hexdigest()

    # Fetch live derived data from mock Platform API via adapter
    # platform_data = await platform_client.get_worker_profile(body.platform_id)
    
    # if platform_data.tenure_days < 30:
    #     income_band = "MID"  # Cold-start rule
    # else:
    #     income_band = platform_data.income_band
        
    worker = Worker(
        name=body.name,
        phone_number=body.phone_number,
        platform_id=body.platform_id,
        # city=platform_data.city,
        # zone_id=platform_data.assigned_zone,
        # income_band=income_band,
        aadhaar_hash=aadhaar_hash,
        kyc_status=KycStatus.MOCK_VERIFIED,
        mandate_status=MandateStatus.INACTIVE,
        mandate_failures=0
    )
    db.add(worker)
    
    # seed BFM Baseline after BFM model is ready
    
    await db.commit()
    await db.refresh(worker)
    return {c.name: getattr(worker, c.name) for c in Worker.__table__.columns}


@router.post("/login", response_model=Token)
async def login_worker(body: WorkerLoginRequest, db: DBSession) -> Token:
    # again
    from ...models.worker import Worker  # Import here to avoid circular imports

    if body.otp != settings.MOCK_OTP:
        raise UnauthorizedException("Invalid OTP.")

    result = await db.execute(select(Worker).where(Worker.phone_number == body.phone_number))
    worker = result.scalar_one_or_none()
    if worker is None:
        raise BadRequestException("Worker not found. Please register first.")

    return Token(
        access_token=await create_access_token({"sub": worker.phone_number}),
        token_type="bearer",
    )


@router.post("/logout", status_code=204)
async def logout_worker(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
    _: Annotated[dict, Depends(get_current_worker)],  # validate token before blacklisting
) -> None:
    await blacklist_token(token, db)
