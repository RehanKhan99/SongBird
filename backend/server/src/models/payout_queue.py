import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import UUIDMixin


class PayoutStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"


class PayoutQueue(UUIDMixin, Base):
    __tablename__ = "payout_queue"

    # required
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("claim.id"), index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2))

    # optional with defaults
    status: Mapped[str] = mapped_column(String(20), default=PayoutStatus.PENDING, index=True)
    razorpay_ref: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
