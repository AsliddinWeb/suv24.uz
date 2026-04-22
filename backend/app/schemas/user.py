from uuid import UUID

from pydantic import BaseModel, Field

from app.models.user import UserRole
from app.schemas.common import ORMModel


class UserOut(ORMModel):
    id: UUID
    company_id: UUID
    phone: str
    full_name: str
    role: UserRole
    is_active: bool


class UserCreate(ORMModel):
    phone: str = Field(min_length=7, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole


class UserUpdate(BaseModel):
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class PasswordResetRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
