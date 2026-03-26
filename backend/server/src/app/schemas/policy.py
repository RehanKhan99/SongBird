import uuid
from datetime import datetime

from pydantic import BaseModel


class PolicyCreate(BaseModel):
    tier: str  # BASIC / STANDARD / PREMIUM


class PolicyRead(BaseModel):
    id: uuid.UUID
    worker_id: uuid.UUID
    tier: str
    base_premium: float
    weekly_premium: float
    status: str
    cooling_off_ends_at: datetime | None
    policy_week: int
    created_at: datetime

    model_config = {"from_attributes": True}
