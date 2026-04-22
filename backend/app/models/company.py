import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class TariffPlan(str, enum.Enum):
    TRIAL = "trial"
    START = "start"
    BIZNES = "biznes"
    PREMIUM = "premium"


class Company(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    short_name: Mapped[str | None] = mapped_column(String(32), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    support_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Tashkent")
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="UZS")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    tariff_plan: Mapped[TariffPlan] = mapped_column(
        SAEnum(
            TariffPlan,
            name="tariff_plan",
            native_enum=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=TariffPlan.TRIAL,
    )
    monthly_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Company {self.slug}>"
