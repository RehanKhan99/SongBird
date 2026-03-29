import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TriggerType(StrEnum):
    A1 = "A1"  # Rain
    A3 = "A3"  # AQI
    A4 = "A4"  # Heat
    B3 = "B3"  # Platform outage

class TriggerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class TriggerEventRead(BaseModel):
    id: uuid.UUID
    trigger_type: TriggerType
    zone_id: str
    threshold_value: float | None
    fired_at: datetime
    closed_at: datetime | None
    status: TriggerStatus

    model_config = {"from_attributes": True}
