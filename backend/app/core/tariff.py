"""Tariff plan limits — enforced when creating drivers, customers, orders."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbDep
from app.models.company import Company, TariffPlan
from app.models.customer import Customer
from app.models.driver import Driver
from app.models.order import Order


@dataclass(frozen=True)
class TariffLimits:
    """None = unlimited."""
    max_drivers: int | None
    max_customers: int | None
    max_orders_per_month: int | None
    label: str


# Limit table — kept here so SaaS pricing and code stay in sync.
LIMITS: dict[TariffPlan, TariffLimits] = {
    TariffPlan.TRIAL: TariffLimits(
        max_drivers=2,
        max_customers=100,
        max_orders_per_month=200,
        label="Sinov",
    ),
    TariffPlan.START: TariffLimits(
        max_drivers=3,
        max_customers=500,
        max_orders_per_month=1000,
        label="Start",
    ),
    TariffPlan.BIZNES: TariffLimits(
        max_drivers=None,
        max_customers=None,
        max_orders_per_month=None,
        label="Biznes",
    ),
    TariffPlan.PREMIUM: TariffLimits(
        max_drivers=None,
        max_customers=None,
        max_orders_per_month=None,
        label="Premium",
    ),
}


@dataclass
class TariffUsage:
    drivers: int
    customers: int
    orders_this_month: int


async def _company_usage(db, company_id: UUID) -> TariffUsage:
    drivers = (
        await db.execute(
            select(func.count())
            .select_from(Driver)
            .where(Driver.company_id == company_id, Driver.deleted_at.is_(None))
        )
    ).scalar_one()
    customers = (
        await db.execute(
            select(func.count())
            .select_from(Customer)
            .where(Customer.company_id == company_id, Customer.deleted_at.is_(None))
        )
    ).scalar_one()
    # First day of current month UTC
    now = datetime.now(tz=timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    orders_month = (
        await db.execute(
            select(func.count())
            .select_from(Order)
            .where(
                Order.company_id == company_id,
                Order.deleted_at.is_(None),
                Order.created_at >= start_of_month,
            )
        )
    ).scalar_one()
    return TariffUsage(int(drivers), int(customers), int(orders_month))


async def _company_for(user, db) -> Company:
    if user.company_id is None:
        raise HTTPException(status_code=403, detail="Kompaniya yo'q")
    company = (
        await db.execute(select(Company).where(Company.id == user.company_id))
    ).scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


def _check_trial_active(company: Company) -> None:
    if (
        company.tariff_plan == TariffPlan.TRIAL
        and company.trial_ends_at is not None
        and company.trial_ends_at < datetime.now(tz=timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Sinov muddati tugagan. Tarif tanlash uchun adminga murojaat qiling.",
        )


def enforce(resource: str):
    """Dependency factory. Use as `_: None = Depends(enforce('drivers'))`."""

    async def _check(user: CurrentUser, db: DbDep) -> None:
        company = await _company_for(user, db)
        _check_trial_active(company)
        limits = LIMITS[company.tariff_plan]
        usage = await _company_usage(db, company.id)

        if resource == "drivers" and limits.max_drivers is not None:
            if usage.drivers >= limits.max_drivers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"{limits.label} tarif chegarasi: {limits.max_drivers} ta haydovchi. "
                        f"Yuqori tarif tanlash uchun adminga murojaat qiling."
                    ),
                )
        elif resource == "customers" and limits.max_customers is not None:
            if usage.customers >= limits.max_customers:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"{limits.label} tarif chegarasi: {limits.max_customers} ta mijoz. "
                        f"Yuqori tarif tanlang."
                    ),
                )
        elif resource == "orders" and limits.max_orders_per_month is not None:
            if usage.orders_this_month >= limits.max_orders_per_month:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"{limits.label} tarif chegarasi: oyiga "
                        f"{limits.max_orders_per_month} ta buyurtma. "
                        f"Yuqori tarif tanlang."
                    ),
                )

    return _check


EnforceDrivers = Annotated[None, Depends(enforce("drivers"))]
EnforceCustomers = Annotated[None, Depends(enforce("customers"))]
EnforceOrders = Annotated[None, Depends(enforce("orders"))]


async def usage_with_limits(user: CurrentUser, db: DbDep) -> dict:
    """For Settings page — show owner what they have vs allowed."""
    company = await _company_for(user, db)
    limits = LIMITS[company.tariff_plan]
    usage = await _company_usage(db, company.id)
    return {
        "tariff_plan": company.tariff_plan.value,
        "tariff_label": limits.label,
        "drivers": {"used": usage.drivers, "limit": limits.max_drivers},
        "customers": {"used": usage.customers, "limit": limits.max_customers},
        "orders_this_month": {
            "used": usage.orders_this_month,
            "limit": limits.max_orders_per_month,
        },
        "trial_ends_at": company.trial_ends_at.isoformat() if company.trial_ends_at else None,
    }
