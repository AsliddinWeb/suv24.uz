import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CompanyScopedMixin, SoftDeleteMixin, TimestampMixin


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrderSource(str, enum.Enum):
    OPERATOR = "operator"
    QR = "qr"
    SUBSCRIPTION = "subscription"
    ADMIN = "admin"


TERMINAL_STATUSES: set[OrderStatus] = {OrderStatus.DELIVERED, OrderStatus.CANCELLED}

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.ASSIGNED, OrderStatus.CANCELLED},
    OrderStatus.ASSIGNED: {OrderStatus.IN_DELIVERY, OrderStatus.PENDING, OrderStatus.CANCELLED},
    OrderStatus.IN_DELIVERY: {OrderStatus.DELIVERED, OrderStatus.FAILED},
    OrderStatus.FAILED: {OrderStatus.PENDING},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}

REASON_REQUIRED: set[OrderStatus] = {OrderStatus.FAILED, OrderStatus.CANCELLED}


_order_status_enum = SAEnum(
    OrderStatus,
    name="order_status",
    native_enum=True,
    values_callable=lambda e: [v.value for v in e],
)

_order_source_enum = SAEnum(
    OrderSource,
    name="order_source",
    native_enum=True,
    values_callable=lambda e: [v.value for v in e],
)


class Order(Base, TimestampMixin, SoftDeleteMixin, CompanyScopedMixin):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("number", name="uq_orders_number"),
    )

    number: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1001, increment=1),
        nullable=False,
    )

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("customer_addresses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    driver_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        _order_status_enum,
        nullable=False,
        default=OrderStatus.PENDING,
    )
    source: Mapped[OrderSource] = mapped_column(
        _order_source_enum,
        nullable=False,
        default=OrderSource.OPERATOR,
    )

    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))

    delivery_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OrderItem.created_at.asc()",
    )
    status_logs: Mapped[list["OrderStatusLog"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OrderStatusLog.created_at.asc()",
    )

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES

    def __repr__(self) -> str:
        return f"<Order #{self.number} {self.status.value}>"


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    # Product name snapshot — so order history remains readable even if product renamed/deleted
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")


class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[OrderStatus | None] = mapped_column(_order_status_enum, nullable=True)
    to_status: Mapped[OrderStatus] = mapped_column(_order_status_enum, nullable=False)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    order: Mapped[Order] = relationship(back_populates="status_logs")
