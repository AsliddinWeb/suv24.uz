from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    short_name: str | None = None
    phone: str | None = None
    support_phone: str | None = None
    address: str | None = None
    logo_url: str | None = None
    timezone: str
    currency: str


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    short_name: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=32)
    support_phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)
    logo_url: str | None = Field(default=None, max_length=512)
