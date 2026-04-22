from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, literal, select

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbDep, require_roles
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/reports", tags=["reports"])

StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


class DailyRevenuePoint(BaseModel):
    date: date
    revenue: Decimal
    orders: int


@router.get("/revenue/daily", response_model=list[DailyRevenuePoint])
async def daily_revenue(
    user: StaffUser,
    db: DbDep,
    days: int = Query(default=7, ge=1, le=90),
) -> list[DailyRevenuePoint]:
    tz = ZoneInfo(get_settings().APP_TIMEZONE)
    today_local = datetime.now(tz=tz).date()
    start_local = today_local - timedelta(days=days - 1)
    start_utc = datetime.combine(start_local, time.min, tzinfo=tz).astimezone(timezone.utc)

    # Group by local date: `created_at AT TIME ZONE 'Asia/Tashkent'` -> then date()
    tz_name = literal(get_settings().APP_TIMEZONE)
    payment_day_expr = func.date(func.timezone(tz_name, Payment.created_at)).label("day")
    revenue_stmt = (
        select(
            payment_day_expr,
            func.coalesce(func.sum(Payment.amount), 0).label("revenue"),
        )
        .where(
            Payment.company_id == user.company_id,
            Payment.deleted_at.is_(None),
            Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
            Payment.created_at >= start_utc,
        )
        .group_by(payment_day_expr)
    )
    revenue_rows = (await db.execute(revenue_stmt)).all()
    revenue_map = {row.day: Decimal(row.revenue) for row in revenue_rows}

    # Orders created per day (local date)
    order_day_expr = func.date(func.timezone(tz_name, Order.created_at)).label("day")
    order_stmt = (
        select(order_day_expr, func.count().label("n"))
        .where(
            Order.company_id == user.company_id,
            Order.deleted_at.is_(None),
            Order.created_at >= start_utc,
        )
        .group_by(order_day_expr)
    )
    order_rows = (await db.execute(order_stmt)).all()
    order_map = {row.day: int(row.n) for row in order_rows}

    points: list[DailyRevenuePoint] = []
    for i in range(days):
        d = today_local - timedelta(days=days - 1 - i)
        points.append(
            DailyRevenuePoint(
                date=d,
                revenue=revenue_map.get(d, Decimal("0.00")),
                orders=order_map.get(d, 0),
            )
        )
    return points


class StatusDistributionItem(BaseModel):
    status: OrderStatus
    count: int


@router.get("/orders/by-status", response_model=list[StatusDistributionItem])
async def orders_by_status(user: CurrentUser, db: DbDep) -> list[StatusDistributionItem]:
    stmt = (
        select(Order.status, func.count().label("n"))
        .where(Order.company_id == user.company_id, Order.deleted_at.is_(None))
        .group_by(Order.status)
    )
    rows = (await db.execute(stmt)).all()
    return [StatusDistributionItem(status=r.status, count=int(r.n)) for r in rows]
