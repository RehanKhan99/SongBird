import uuid
from enum import StrEnum

from pydantic import BaseModel


class IncomeBand(StrEnum):
    LOW = "LOW"
    MID = "MID"
    HIGH = "HIGH"
    ULTRA = "ULTRA"
    # about the above instead of tieing to bands why
    # not accoding to income levels needs more thinking on this
    # cause someone might be too low even for the low band
    # or too high even for the utlra band


class KycStatus(StrEnum):
    MOCK_VERIFIED = "mock_verified"
    VERIFIED = "verified"
    PENDING = "pending"
    REJECTED = "rejected"


class MandateStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FAILING = "FAILING"
    PAUSED = "PAUSED"


class WorkerRegister(BaseModel):
    name: str
    phone_number: str
    platform_id: str
    aadhaar_last4: str  # mock KYC last 4 digits only


class WorkerLoginRequest(BaseModel):
    phone_number: str
    otp: str


class WorkerRead(BaseModel):
    id: uuid.UUID
    name: str
    phone_number: str
    platform_id: str
    city: str | None          # None until PlatformClient DI is wired
    zone_id: str | None
    income_band: IncomeBand | None
    kyc_status: KycStatus
    mandate_status: MandateStatus
    mandate_failures: int
    auto_renew_tier: str | None

    model_config = {"from_attributes": True}
