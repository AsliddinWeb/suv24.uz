from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.payment import PaymentMethod, PaymentStatus
from app.schemas.common import ORMModel


class PaymentCreate(BaseModel):
    order_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    method: PaymentMethod
    notes: str | None = None
    provider_tx_id: str | None = Field(default=None, max_length=128)


class RefundRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class PaymentOut(ORMModel):
    id: UUID
    company_id: UUID
    order_id: UUID
    customer_id: UUID
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    provider_tx_id: str | None
    recorded_by_user_id: UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class DailyCashSummary(BaseModel):
    date: date
    driver_id: UUID | None
    total_cash: Decimal
    total_card_manual: Decimal
    count: int
