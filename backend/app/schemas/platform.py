from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.company import TariffPlan


class PlatformCompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    short_name: str | None = None
    phone: str | None = None
    support_phone: str | None = None
    address: str | None = None
    logo_url: str | None = None
    tariff_plan: TariffPlan
    monthly_fee: Decimal
    trial_ends_at: datetime | None = None
    is_active: bool
    timezone: str
    currency: str
    created_at: datetime


class PlatformCompanyStats(BaseModel):
    users_count: int
    drivers_count: int
    customers_count: int
    orders_total: int
    orders_this_month: int
    revenue_this_month: Decimal


class PlatformCompanyDetail(PlatformCompanyOut):
    stats: PlatformCompanyStats


class PlatformCompanyCreate(BaseModel):
    # Company
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]*$")
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)
    tariff_plan: TariffPlan = TariffPlan.TRIAL
    monthly_fee: Decimal = Decimal("0.00")
    trial_ends_at: datetime | None = None
    # First super admin
    admin_full_name: str = Field(min_length=1, max_length=255)
    admin_phone: str = Field(min_length=5, max_length=32)
    admin_password: str = Field(min_length=6, max_length=128)


class PlatformCompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    short_name: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=32)
    support_phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)
    logo_url: str | None = Field(default=None, max_length=512)
    tariff_plan: TariffPlan | None = None
    monthly_fee: Decimal | None = None
    trial_ends_at: datetime | None = None
    is_active: bool | None = None


class PlatformOverview(BaseModel):
    companies_total: int
    companies_active: int
    companies_trial: int
    platform_mrr: Decimal  # sum of monthly_fee across active companies
    orders_this_month: int
    revenue_this_month: Decimal  # across all tenants
    tariff_breakdown: dict[str, int]
    top_companies_by_revenue: list["PlatformTopCompany"]


class PlatformTopCompany(BaseModel):
    id: UUID
    name: str
    slug: str
    tariff_plan: TariffPlan
    revenue_this_month: Decimal
    orders_this_month: int


PlatformOverview.model_rebuild()
