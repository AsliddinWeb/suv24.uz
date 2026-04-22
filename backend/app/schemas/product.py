from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PriceOut(ORMModel):
    id: UUID
    product_id: UUID
    price: Decimal
    valid_from: datetime
    valid_to: datetime | None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    volume_liters: int = Field(gt=0, le=100)
    is_returnable: bool = True
    is_active: bool = True
    initial_price: Decimal = Field(gt=0, decimal_places=2)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    volume_liters: int | None = Field(default=None, gt=0, le=100)
    is_returnable: bool | None = None
    is_active: bool | None = None


class PriceCreate(BaseModel):
    price: Decimal = Field(gt=0, decimal_places=2)


class ProductOut(ORMModel):
    id: UUID
    company_id: UUID
    name: str
    volume_liters: int
    is_returnable: bool
    is_active: bool
    current_price: Decimal | None
