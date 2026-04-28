from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CompanyScopedMixin, TimestampMixin


class WarehouseStock(Base, TimestampMixin, CompanyScopedMixin):
    """Total stock physically in the company warehouse — separate from driver
    balances and customer bottle debt.

    Reconciliation invariant:
        total_company_bottles
            = warehouse.full + warehouse.empty
            + sum(driver.full + driver.empty)
            + sum(customer.bottle_debt)   # bottles out at customers
    """

    __tablename__ = "warehouse_stock"
    __table_args__ = (
        UniqueConstraint("company_id", "product_id", name="uq_warehouse_company_product"),
        CheckConstraint("full_count >= 0", name="ck_warehouse_full_nonneg"),
        CheckConstraint("empty_count >= 0", name="ck_warehouse_empty_nonneg"),
    )

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    empty_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class StockMovement(Base, TimestampMixin, CompanyScopedMixin):
    """Audit log for warehouse stock changes — useful for reconciliation."""

    __tablename__ = "stock_movements"

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Movement kind: 'initial', 'purchase', 'load_driver', 'return_driver',
    # 'refill', 'manual', 'loss'
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    full_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    empty_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    driver_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
