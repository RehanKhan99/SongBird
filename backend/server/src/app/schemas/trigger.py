import uuid
from datetime import datetime

from pydantic import BaseModel


class TriggerEventRead(BaseModel):
    id: uuid.UUID
    trigger_type: str  # For now : A1 / A3 / A4 / B3 only
    zone_id: str
    threshold_value: float | None
    fired_at: datetime
    closed_at: datetime | None
    status: str  # ACTIVE / CLOSED

    model_config = {"from_attributes": True}
