from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.customer import CustomerSegment
from app.schemas.common import ORMModel


class CustomerCreate(BaseModel):
    phone: str = Field(min_length=7, max_length=32)
    full_name: str = Field(min_length=1, max_length=255)
    segment: CustomerSegment = CustomerSegment.NEW
    notes: str | None = None


class CustomerUpdate(BaseModel):
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    segment: CustomerSegment | None = None
    notes: str | None = None


class CustomerOut(ORMModel):
    id: UUID
    company_id: UUID
    phone: str
    full_name: str
    segment: CustomerSegment
    notes: str | None
    balance: Decimal
    bottle_debt: int
