from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AddressCreate(BaseModel):
    label: str = Field(default="Uy", max_length=64)
    address_text: str = Field(min_length=1)
    lat: Decimal | None = Field(default=None, ge=-90, le=90)
    lng: Decimal | None = Field(default=None, ge=-180, le=180)
    notes: str | None = None


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=64)
    address_text: str | None = Field(default=None, min_length=1)
    lat: Decimal | None = Field(default=None, ge=-90, le=90)
    lng: Decimal | None = Field(default=None, ge=-180, le=180)
    is_active: bool | None = None
    notes: str | None = None


class AddressOut(ORMModel):
    id: UUID
    customer_id: UUID
    label: str
    address_text: str
    lat: Decimal | None
    lng: Decimal | None
    qr_token: str
    is_active: bool
    notes: str | None
