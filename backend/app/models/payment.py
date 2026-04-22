import enum
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CompanyScopedMixin, SoftDeleteMixin, TimestampMixin


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD_MANUAL = "card_manual"
    PAYME = "payme"
    CLICK = "click"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    PARTIAL = "partial"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


SETTLED_STATUSES: set[PaymentStatus] = {PaymentStatus.PAID, PaymentStatus.PARTIAL}


_method_enum = SAEnum(
    PaymentMethod,
    name="payment_method",
    native_enum=True,
    values_callable=lambda e: [v.value for v in e],
)

_status_enum = SAEnum(
    PaymentStatus,
    name="payment_status",
    native_enum=True,
    values_callable=lambda e: [v.value for v in e],
)


class Payment(Base, TimestampMixin, SoftDeleteMixin, CompanyScopedMixin):
    __tablename__ = "payments"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(_method_enum, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(_status_enum, nullable=False)

    provider_tx_id: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    recorded_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Payment {self.amount} {self.method.value} {self.status.value}>"
