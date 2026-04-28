from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WarehouseStockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    full_count: int
    empty_count: int
    updated_at: datetime


class WarehouseStockWithProduct(WarehouseStockOut):
    product_name: str
    volume_liters: int
    is_returnable: bool


class WarehouseAdjust(BaseModel):
    """Manual warehouse correction (initial stock entry, refill, loss, etc.)."""
    product_id: UUID
    full_delta: int = 0
    empty_delta: int = 0
    reason: str | None = Field(default=None, max_length=255)


class WarehouseTransfer(BaseModel):
    """Atomic transfer between warehouse and driver."""
    driver_id: UUID
    product_id: UUID
    full_count: int = Field(default=0, ge=0)
    empty_count: int = Field(default=0, ge=0)
    reason: str | None = Field(default=None, max_length=255)


class StockMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    kind: str
    full_delta: int
    empty_delta: int
    driver_id: UUID | None = None
    reason: str | None = None
    actor_user_id: UUID | None = None
    occurred_at: datetime


class WarehouseSummary(BaseModel):
    """Whole-company reconciliation snapshot per product."""
    product_id: UUID
    product_name: str
    volume_liters: int
    warehouse_full: int
    warehouse_empty: int
    drivers_full: int
    drivers_empty: int
    customer_debt: int
    total_in_system: int  # warehouse + drivers + customer_debt
