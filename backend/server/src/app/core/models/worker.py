from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base
from ..core.db.models import TimestampMixin, UUIDMixin
from ..schemas.worker import KycStatus, MandateStatus


class Worker(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "worker"

    # required
    name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    aadhaar_hash: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 hex
    platform_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # Populated via PlatformClientDependency
    # nullable until DI is implemented
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zone_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    income_band: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # system-set
    kyc_status: Mapped[str] = mapped_column(String(20), default=KycStatus.MOCK_VERIFIED)
    
    # auto-mandate tracking
    mandate_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auto_renew_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mandate_status: Mapped[str] = mapped_column(String(20), default=MandateStatus.INACTIVE)
    mandate_failures: Mapped[int] = mapped_column(Integer, default=0)
