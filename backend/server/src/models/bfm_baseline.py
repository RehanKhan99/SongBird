import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import UUIDMixin


class BfmBaseline(UUIDMixin, Base):
    __tablename__ = "bfm_baseline"
    __table_args__ = (UniqueConstraint("worker_id", name="uq_bfm_worker"),)

    # required
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("worker.id"), index=True
    )

    # optional with defaults
    zone_polygon: Mapped[WKBElement | None] = mapped_column(
        Geometry("POLYGON", srid=4326), nullable=True, default=None
    )
    temporal_matrix: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    velocity_baseline: Mapped[float | None] = mapped_column(
        Numeric(8, 4), nullable=True, default=None
    )
    avg_delivery_rate: Mapped[float | None] = mapped_column(
        Numeric(8, 2), nullable=True, default=None
    )
    zts: Mapped[float] = mapped_column(Numeric(5, 2), default=50.0)    # Zone Trust Score 0-100
    bds: Mapped[float] = mapped_column(Numeric(5, 4), default=0.60)    # Behavioral Deviation 0-1
    is_seeded: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), init=False
    )
