from uuid import UUID

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DriverBottleBalance(Base, TimestampMixin):
    __tablename__ = "driver_bottle_balance"
    __table_args__ = (
        UniqueConstraint("driver_id", "product_id", name="uq_driver_bottle_driver_product"),
    )

    driver_id: Mapped[UUID] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    full_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    empty_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"<DriverBottleBalance driver={self.driver_id} product={self.product_id} "
            f"full={self.full_count} empty={self.empty_count}>"
        )
