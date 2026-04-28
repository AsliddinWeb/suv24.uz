from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbDep
from app.core.security import hash_password
from app.core.tariff import tariffs_meta
from app.models.company import Company, TariffPlan
from app.models.customer import Customer
from app.models.driver import Driver
from app.models.order import Order
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.schemas.platform import (
    PlatformCompanyCreate,
    PlatformCompanyDetail,
    PlatformCompanyOut,
    PlatformCompanyStats,
    PlatformCompanyUpdate,
    PlatformOverview,
    PlatformTopCompany,
)

router = APIRouter(prefix="/platform", tags=["platform"])


async def require_platform_owner(user: CurrentUser) -> User:
    if user.role != UserRole.PLATFORM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform owner only",
        )
    return user


PlatformOwner = Annotated[User, Depends(require_platform_owner)]


def _month_bounds_utc() -> tuple[datetime, datetime]:
    tz = ZoneInfo(get_settings().APP_TIMEZONE)
    now_local = datetime.now(tz=tz)
    start_local = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start_local.month == 12:
        next_month = start_local.replace(year=start_local.year + 1, month=1)
    else:
        next_month = start_local.replace(month=start_local.month + 1)
    return (
        start_local.astimezone(timezone.utc),
        next_month.astimezone(timezone.utc),
    )


async def _company_stats(db, company_id: UUID) -> PlatformCompanyStats:
    start_utc, end_utc = _month_bounds_utc()

    users_q = select(func.count()).select_from(User).where(
        User.company_id == company_id,
        User.deleted_at.is_(None),
    )
    drivers_q = select(func.count()).select_from(Driver).where(
        Driver.company_id == company_id,
        Driver.deleted_at.is_(None),
    )
    customers_q = select(func.count()).select_from(Customer).where(
        Customer.company_id == company_id,
        Customer.deleted_at.is_(None),
    )
    orders_total_q = select(func.count()).select_from(Order).where(
        Order.company_id == company_id,
        Order.deleted_at.is_(None),
    )
    orders_month_q = select(func.count()).select_from(Order).where(
        Order.company_id == company_id,
        Order.deleted_at.is_(None),
        Order.created_at >= start_utc,
        Order.created_at < end_utc,
    )
    revenue_month_q = select(func.coalesce(func.sum(Payment.amount), 0)).where(
        Payment.company_id == company_id,
        Payment.deleted_at.is_(None),
        Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
        Payment.created_at >= start_utc,
        Payment.created_at < end_utc,
    )

    users_count = (await db.execute(users_q)).scalar_one()
    drivers_count = (await db.execute(drivers_q)).scalar_one()
    customers_count = (await db.execute(customers_q)).scalar_one()
    orders_total = (await db.execute(orders_total_q)).scalar_one()
    orders_month = (await db.execute(orders_month_q)).scalar_one()
    revenue_month = (await db.execute(revenue_month_q)).scalar_one()

    return PlatformCompanyStats(
        users_count=int(users_count),
        drivers_count=int(drivers_count),
        customers_count=int(customers_count),
        orders_total=int(orders_total),
        orders_this_month=int(orders_month),
        revenue_this_month=Decimal(revenue_month or 0),
    )


@router.get("/overview", response_model=PlatformOverview)
async def get_overview(_: PlatformOwner, db: DbDep) -> PlatformOverview:
    start_utc, end_utc = _month_bounds_utc()

    companies = (
        await db.execute(
            select(Company).where(Company.deleted_at.is_(None)).order_by(Company.created_at)
        )
    ).scalars().all()

    companies_active = sum(1 for c in companies if c.is_active)
    companies_trial = sum(1 for c in companies if c.tariff_plan == TariffPlan.TRIAL)

    platform_mrr = sum(
        (c.monthly_fee for c in companies if c.is_active),
        Decimal("0.00"),
    )

    tariff_breakdown: dict[str, int] = {t.value: 0 for t in TariffPlan}
    for c in companies:
        tariff_breakdown[c.tariff_plan.value] += 1

    orders_month_q = select(func.count()).select_from(Order).where(
        Order.deleted_at.is_(None),
        Order.created_at >= start_utc,
        Order.created_at < end_utc,
    )
    revenue_month_q = select(func.coalesce(func.sum(Payment.amount), 0)).where(
        Payment.deleted_at.is_(None),
        Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
        Payment.created_at >= start_utc,
        Payment.created_at < end_utc,
    )
    orders_month = (await db.execute(orders_month_q)).scalar_one()
    revenue_month = (await db.execute(revenue_month_q)).scalar_one()

    # Top 5 by revenue this month
    top_q = (
        select(
            Company.id,
            Company.name,
            Company.slug,
            Company.tariff_plan,
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
            func.count(Payment.id.distinct()).label("pay_count"),
        )
        .join(Payment, Payment.company_id == Company.id, isouter=True)
        .where(
            Company.deleted_at.is_(None),
            (Payment.deleted_at.is_(None)) | (Payment.id.is_(None)),
        )
        .where(
            (Payment.created_at.is_(None))
            | (
                (Payment.created_at >= start_utc)
                & (Payment.created_at < end_utc)
                & (Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]))
            )
        )
        .group_by(Company.id, Company.name, Company.slug, Company.tariff_plan)
        .order_by(func.coalesce(func.sum(Payment.amount), 0).desc())
        .limit(5)
    )
    top_rows = (await db.execute(top_q)).all()

    # orders_this_month per top company (separate query so isolated)
    tops: list[PlatformTopCompany] = []
    for row in top_rows:
        oc_q = select(func.count()).select_from(Order).where(
            Order.company_id == row.id,
            Order.deleted_at.is_(None),
            Order.created_at >= start_utc,
            Order.created_at < end_utc,
        )
        orders_n = (await db.execute(oc_q)).scalar_one()
        tops.append(
            PlatformTopCompany(
                id=row.id,
                name=row.name,
                slug=row.slug,
                tariff_plan=row.tariff_plan,
                revenue_this_month=Decimal(row.revenue or 0),
                orders_this_month=int(orders_n),
            )
        )

    return PlatformOverview(
        companies_total=len(companies),
        companies_active=companies_active,
        companies_trial=companies_trial,
        platform_mrr=platform_mrr,
        orders_this_month=int(orders_month),
        revenue_this_month=Decimal(revenue_month or 0),
        tariff_breakdown=tariff_breakdown,
        top_companies_by_revenue=tops,
    )


@router.get("/companies", response_model=list[PlatformCompanyOut])
async def list_companies(
    _: PlatformOwner,
    db: DbDep,
    q: str | None = Query(default=None, description="search by name/slug"),
    active: bool | None = Query(default=None),
) -> list[PlatformCompanyOut]:
    stmt = select(Company).where(Company.deleted_at.is_(None)).order_by(Company.created_at.desc())
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (func.lower(Company.name).like(like)) | (func.lower(Company.slug).like(like))
        )
    if active is not None:
        stmt = stmt.where(Company.is_active == active)
    rows = (await db.execute(stmt)).scalars().all()
    return [PlatformCompanyOut.model_validate(c) for c in rows]


@router.post("/companies", response_model=PlatformCompanyDetail, status_code=201)
async def create_company(
    payload: PlatformCompanyCreate,
    _: PlatformOwner,
    db: DbDep,
) -> PlatformCompanyDetail:
    company = Company(
        name=payload.name,
        slug=payload.slug,
        phone=payload.phone,
        address=payload.address,
        tariff_plan=payload.tariff_plan,
        monthly_fee=payload.monthly_fee,
        trial_ends_at=payload.trial_ends_at,
        timezone=get_settings().APP_TIMEZONE,
        currency="UZS",
        is_active=True,
    )
    db.add(company)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bunday slug allaqachon band",
        )

    admin = User(
        company_id=company.id,
        phone=payload.admin_phone,
        password_hash=hash_password(payload.admin_password),
        full_name=payload.admin_full_name,
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    db.add(admin)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin telefoni band",
        )

    await db.commit()
    await db.refresh(company)
    stats = await _company_stats(db, company.id)
    return PlatformCompanyDetail(
        **PlatformCompanyOut.model_validate(company).model_dump(),
        stats=stats,
    )


@router.get("/companies/{company_id}", response_model=PlatformCompanyDetail)
async def get_company(company_id: UUID, _: PlatformOwner, db: DbDep) -> PlatformCompanyDetail:
    company = (
        await db.execute(
            select(Company).where(Company.id == company_id, Company.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    stats = await _company_stats(db, company.id)
    return PlatformCompanyDetail(
        **PlatformCompanyOut.model_validate(company).model_dump(),
        stats=stats,
    )


@router.patch("/companies/{company_id}", response_model=PlatformCompanyOut)
async def update_company(
    company_id: UUID,
    payload: PlatformCompanyUpdate,
    _: PlatformOwner,
    db: DbDep,
) -> PlatformCompanyOut:
    company = (
        await db.execute(
            select(Company).where(Company.id == company_id, Company.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(company, field, value)

    await db.flush()
    await db.commit()
    await db.refresh(company)
    return PlatformCompanyOut.model_validate(company)


@router.get("/tariffs")
async def list_tariffs(_: PlatformOwner) -> list[dict]:
    """Static catalog of tariff plans + their limits and features."""
    return tariffs_meta()


# ----- Company super-admin management -----


class CompanyAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime


class CompanyAdminUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=5, max_length=32)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    is_active: bool | None = None


@router.get("/companies/{company_id}/admins", response_model=list[CompanyAdminOut])
async def list_company_admins(
    company_id: UUID, _: PlatformOwner, db: DbDep
) -> list[CompanyAdminOut]:
    rows = (
        await db.execute(
            select(User)
            .where(
                User.company_id == company_id,
                User.role == UserRole.SUPER_ADMIN,
                User.deleted_at.is_(None),
            )
            .order_by(User.created_at)
        )
    ).scalars().all()
    return [CompanyAdminOut.model_validate(u) for u in rows]


@router.patch(
    "/companies/{company_id}/admins/{user_id}", response_model=CompanyAdminOut
)
async def update_company_admin(
    company_id: UUID,
    user_id: UUID,
    payload: CompanyAdminUpdate,
    _: PlatformOwner,
    db: DbDep,
) -> CompanyAdminOut:
    target = (
        await db.execute(
            select(User).where(
                User.id == user_id,
                User.company_id == company_id,
                User.role == UserRole.SUPER_ADMIN,
                User.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="Super admin not found")

    data = payload.model_dump(exclude_unset=True)
    if "phone" in data and data["phone"] != target.phone:
        clashing = (
            await db.execute(
                select(User).where(
                    User.company_id == company_id,
                    User.phone == data["phone"],
                    User.deleted_at.is_(None),
                    User.id != user_id,
                )
            )
        ).scalar_one_or_none()
        if clashing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bu telefon raqami band",
            )
        target.phone = data["phone"]
    if "full_name" in data:
        target.full_name = data["full_name"]
    if "password" in data and data["password"]:
        target.password_hash = hash_password(data["password"])
    if "is_active" in data and data["is_active"] is not None:
        target.is_active = data["is_active"]

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Konflikt")

    await db.commit()
    await db.refresh(target)
    return CompanyAdminOut.model_validate(target)


@router.delete("/companies/{company_id}", status_code=204)
async def delete_company(company_id: UUID, _: PlatformOwner, db: DbDep) -> Response:
    company = (
        await db.execute(
            select(Company).where(Company.id == company_id, Company.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    now = datetime.now(tz=timezone.utc)
    company.deleted_at = now
    company.is_active = False
    # Also soft-delete related users so they can't log in
    await db.execute(
        User.__table__.update()
        .where(User.company_id == company_id, User.deleted_at.is_(None))
        .values(deleted_at=now, is_active=False)
    )
    await db.commit()
    return Response(status_code=204)
