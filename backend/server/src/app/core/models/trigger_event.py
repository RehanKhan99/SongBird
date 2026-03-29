from datetime import datetime

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import TimestampMixin, UUIDMixin
from ..schemas.trigger import TriggerStatus


class TriggerEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "trigger_event"

    # required
    trigger_type: Mapped[str] = mapped_column(String(10), index=True)
    zone_id: Mapped[str] = mapped_column(String(100), index=True)

    # optional with defaults
    threshold_value: Mapped[float | None] = mapped_column(
        Numeric(8, 4), nullable=True, default=None
    )
    status: Mapped[str] = mapped_column(String(20), default=TriggerStatus.ACTIVE, index=True)
    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, init=False  # populated at trigger fire time
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
