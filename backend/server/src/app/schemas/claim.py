import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ClaimDecision(StrEnum):
    AUTO_APPROVE = "AUTO_APPROVE"
    CONDITIONAL = "CONDITIONAL"
    HOLD = "HOLD"
    REJECT = "REJECT"


class ClaimRead(BaseModel):
    id: uuid.UUID
    worker_id: uuid.UUID
    policy_id: uuid.UUID
    trigger_event_id: uuid.UUID
    cfs_score: float | None
    cfs_signals: dict | None
    decision: ClaimDecision | None # AUTO_APPROVE / CONDITIONAL(2HR SLA) / HOLD(4HR SLA) / REJECT
    payout_amount: float | None
    reason_codes: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
