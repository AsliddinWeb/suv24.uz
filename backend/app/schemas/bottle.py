from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class BottleBalanceOut(ORMModel):
    id: UUID
    driver_id: UUID
    product_id: UUID
    full_count: int
    empty_count: int


class BottleBalanceWithProduct(BottleBalanceOut):
    product_name: str
    volume_liters: int


class BottleAdjustRequest(BaseModel):
    product_id: UUID
    full_delta: int = Field(default=0)
    empty_delta: int = Field(default=0)
    reason: str | None = Field(default=None, max_length=200)


class BottleReturn(BaseModel):
    product_id: UUID
    count: int = Field(gt=0, le=1000)


class DeliverRequest(BaseModel):
    bottle_returns: list[BottleReturn] = Field(default_factory=list, max_length=20)
