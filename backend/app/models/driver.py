from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CompanyScopedMixin, SoftDeleteMixin, TimestampMixin
from app.models.user import User


class Driver(Base, TimestampMixin, SoftDeleteMixin, CompanyScopedMixin):
    __tablename__ = "drivers"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    vehicle_plate: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    current_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    current_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"<Driver user={self.user_id} plate={self.vehicle_plate}>"
