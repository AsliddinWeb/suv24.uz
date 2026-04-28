from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.cash import CashTransactionKind


class CashAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    balance: Decimal
    currency: str
    opening_set_at: datetime | None = None


class OpeningBalanceIn(BaseModel):
    amount: Decimal = Field(ge=0)
    note: str | None = Field(default=None, max_length=255)


class ExpenseIn(BaseModel):
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    occurred_at: datetime | None = None


class ManualCashIn(BaseModel):
    """Owner injection / extra income / write-off."""
    direction: str = Field(pattern="^(in|out)$")
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    occurred_at: datetime | None = None


class PurchaseIn(BaseModel):
    product_id: UUID
    full_count: int = Field(default=0, ge=0)
    empty_count: int = Field(default=0, ge=0)
    unit_cost: Decimal = Field(ge=0)
    supplier: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=512)
    occurred_at: datetime | None = None


class PurchaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name: str | None = None
    volume_liters: int | None = None
    full_count: int
    empty_count: int
    unit_cost: Decimal
    total_cost: Decimal
    supplier: str | None = None
    note: str | None = None
    occurred_at: datetime
    actor_user_id: UUID | None = None
    created_at: datetime


class CashTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: CashTransactionKind
    amount: Decimal
    description: str | None = None
    occurred_at: datetime
    actor_user_id: UUID | None = None
    related_purchase_id: UUID | None = None
    related_payment_id: UUID | None = None
    created_at: datetime


class CashSnapshot(BaseModel):
    """Combined balance + recent transactions for the Ombor page header."""
    account: CashAccountOut
    recent: list[CashTransactionOut]
    needs_opening_balance: bool
