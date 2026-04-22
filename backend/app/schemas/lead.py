from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    """Public payload from the landing demo form."""

    full_name: str = Field(min_length=2, max_length=255)
    phone: str = Field(min_length=5, max_length=32)
    company_name: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    source: str = Field(default="landing", max_length=64)


class LeadUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, min_length=5, max_length=32)
    company_name: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    status: LeadStatus | None = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    phone: str
    company_name: str | None = None
    source: str
    notes: str | None = None
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadAck(BaseModel):
    """Response sent to the public after submitting a demo request."""

    id: UUID
    message: str = "Arizangiz qabul qilindi, tez orada bog'lanamiz"
