import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import TimestampMixin, UUIDMixin
from ..schemas.policy import PolicyStatus, PolicyTier


class Policy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "policy"

    # required
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("worker.id"), index=True
    )
    base_premium: Mapped[float] = mapped_column(Numeric(10, 2))
    weekly_premium: Mapped[float] = mapped_column(Numeric(10, 2))

    # optional with defaults
    tier: Mapped[str] = mapped_column(String(20))  # BASIC/STANDARD/PREMIUM — required at creation
    status: Mapped[str] = mapped_column(String(20), default=PolicyStatus.ACTIVE, index=True)
    policy_week: Mapped[int] = mapped_column(Integer, default=1)
    cooling_off_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
