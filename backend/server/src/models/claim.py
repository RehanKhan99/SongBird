import uuid

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import TimestampMixin, UUIDMixin


class Claim(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "claim"

    # required
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("worker.id"), index=True
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("policy.id"), index=True
    )
    trigger_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trigger_event.id"), index=True
    )

    # populated by CFS engine
    cfs_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True, default=None)
    cfs_signals: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    decision: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None, index=True
    )
    payout_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=None)
    reason_codes: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
