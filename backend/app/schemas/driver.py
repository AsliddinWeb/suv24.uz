from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class DriverCreate(BaseModel):
    user_id: UUID
    vehicle_plate: str | None = Field(default=None, max_length=32)


class DriverUpdate(BaseModel):
    vehicle_plate: str | None = Field(default=None, max_length=32)
    is_active: bool | None = None


class DriverOut(ORMModel):
    id: UUID
    company_id: UUID
    user_id: UUID
    vehicle_plate: str | None
    is_active: bool
    current_lat: Decimal | None
    current_lng: Decimal | None
    last_seen_at: datetime | None


class DriverWithUserOut(DriverOut):
    full_name: str
    phone: str
