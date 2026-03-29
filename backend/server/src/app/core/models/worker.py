from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import TimestampMixin, UUIDMixin
from ..schemas.worker import KycStatus


class Worker(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "worker"

    # required
    name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    aadhaar_hash: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 hex
    platform_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    city: Mapped[str] = mapped_column(String(100))
    zone_id: Mapped[str] = mapped_column(String(100), index=True)
    income_band: Mapped[str] = mapped_column(String(10)) 

    # system-set
    kyc_status: Mapped[str] = mapped_column(String(20), default=KycStatus.MOCK_VERIFIED)
