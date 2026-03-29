import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class PolicyTier(StrEnum):
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


class PolicyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class PolicyCreate(BaseModel):
    tier: PolicyTier


class PolicyAutoRenewToggle(BaseModel):
    auto_renew_enabled: bool
    tier: PolicyTier


class PolicyRead(BaseModel):
    id: uuid.UUID
    worker_id: uuid.UUID
    tier: PolicyTier
    base_premium: float
    weekly_premium: float
    status: PolicyStatus
    auto_renew_enabled: bool
    cooling_off_ends_at: datetime | None
    policy_week: int
    created_at: datetime

    model_config = {"from_attributes": True}
