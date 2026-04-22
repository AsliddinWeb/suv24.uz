from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.order import OrderSource, OrderStatus
from app.schemas.common import ORMModel



class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0, le=1000)


class OrderCreate(BaseModel):
    customer_id: UUID
    address_id: UUID
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)
    delivery_window_start: datetime | None = None
    delivery_window_end: datetime | None = None
    notes: str | None = None
    source: OrderSource = OrderSource.OPERATOR

    @model_validator(mode="after")
    def _check_window(self) -> "OrderCreate":
        if self.delivery_window_start and self.delivery_window_end:
            if self.delivery_window_end <= self.delivery_window_start:
                raise ValueError("delivery_window_end must be after delivery_window_start")
        return self


class OrderUpdate(BaseModel):
    delivery_window_start: datetime | None = None
    delivery_window_end: datetime | None = None
    notes: str | None = None


class AssignDriverRequest(BaseModel):
    driver_id: UUID


class ReasonRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class OrderItemOut(ORMModel):
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total: Decimal


class OrderStatusLogOut(ORMModel):
    id: UUID
    from_status: OrderStatus | None
    to_status: OrderStatus
    actor_user_id: UUID | None
    reason: str | None
    created_at: datetime


class CustomerShortOut(ORMModel):
    id: UUID
    full_name: str
    phone: str


class AddressShortOut(ORMModel):
    id: UUID
    label: str
    address_text: str
    lat: Decimal | None
    lng: Decimal | None


class OrderOut(ORMModel):
    id: UUID
    number: int
    company_id: UUID
    customer_id: UUID
    address_id: UUID
    driver_id: UUID | None
    created_by_user_id: UUID | None
    status: OrderStatus
    source: OrderSource
    total: Decimal
    paid_amount: Decimal = Decimal("0")
    delivery_window_start: datetime | None
    delivery_window_end: datetime | None
    notes: str | None
    cancel_reason: str | None
    created_at: datetime
    updated_at: datetime
    customer: CustomerShortOut | None = None
    address: AddressShortOut | None = None


class OrderDetailOut(OrderOut):
    items: list[OrderItemOut]
    status_logs: list[OrderStatusLogOut]
