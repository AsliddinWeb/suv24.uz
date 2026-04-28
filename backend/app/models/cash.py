import enum
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CompanyScopedMixin, TimestampMixin


class CashTransactionKind(str, enum.Enum):
    OPENING_BALANCE = "opening_balance"  # initial entry, can only happen once
    PURCHASE = "purchase"                # warehouse purchase: cash OUT
    EXPENSE = "expense"                  # generic operating expense: cash OUT
    CUSTOMER_PAYMENT = "customer_payment"  # customer paid for an order: cash IN
    REFUND = "refund"                    # refunded to customer: cash OUT
    MANUAL_IN = "manual_in"              # manual cash IN (extra income, owner injection)
    MANUAL_OUT = "manual_out"            # manual cash OUT (write-off, theft)


class CashAccount(Base, TimestampMixin, CompanyScopedMixin):
    """Single cash account per company. balance is denormalized = sum(transactions)."""

    __tablename__ = "cash_accounts"

    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="UZS")
    opening_set_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CashTransaction(Base, TimestampMixin, CompanyScopedMixin):
    """Append-only ledger of every change to the cash balance. amount is signed:
    positive = IN, negative = OUT."""

    __tablename__ = "cash_transactions"

    kind: Mapped[CashTransactionKind] = mapped_column(
        SAEnum(
            CashTransactionKind,
            name="cash_transaction_kind",
            native_enum=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Optional links for traceability
    related_purchase_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory_purchases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    related_payment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


class InventoryPurchase(Base, TimestampMixin, CompanyScopedMixin):
    """A warehouse goods receipt — products coming IN with cost OUT."""

    __tablename__ = "inventory_purchases"

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    empty_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
