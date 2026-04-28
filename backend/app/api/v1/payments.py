from datetime import date, datetime, time, timezone
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbDep, require_roles
from app.models.payment import PaymentMethod, PaymentStatus
from app.models.user import User, UserRole
from app.repositories.payment import PaymentRepository
from app.schemas.pagination import Page, PageParams
from app.schemas.payment import DailyCashSummary, PaymentCreate, PaymentOut, RefundRequest
from app.services.payment import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])

Recorder = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.DRIVER,
        )
    ),
]

StaffAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


@router.get("", response_model=Page[PaymentOut])
async def list_payments(
    user: CurrentUser,
    db: DbDep,
    order_id: UUID | None = Query(default=None),
    customer_id: UUID | None = Query(default=None),
    method: PaymentMethod | None = Query(default=None),
    payment_status: PaymentStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[PaymentOut]:
    params = PageParams(page=page, page_size=page_size)
    items, total = await PaymentRepository(db).list_paginated(
        user.company_id,
        order_id=order_id,
        customer_id=customer_id,
        method=method,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
        offset=params.offset,
        limit=params.limit,
    )
    return Page[PaymentOut](
        items=[PaymentOut.model_validate(p) for p in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def record_payment(
    payload: PaymentCreate,
    user: Recorder,
    db: DbDep,
) -> PaymentOut:
    from decimal import Decimal as _Dec

    from app.api.v1.cash import _get_or_create_account, _record
    from app.models.cash import CashTransactionKind
    from app.models.payment import PaymentStatus as _PS

    service = PaymentService(db)
    payment = await service.record_payment(
        company_id=user.company_id,
        actor_user_id=user.id,
        data=payload,
    )

    # Record cash IN for paid/partial payments. Refunds are reversed elsewhere.
    if payment.status in (_PS.PAID, _PS.PARTIAL):
        amount = _Dec(payment.amount)
        if amount > 0:
            acc = await _get_or_create_account(db, user.company_id)
            _record(
                db,
                account=acc,
                kind=CashTransactionKind.CUSTOMER_PAYMENT,
                amount=amount,
                description=f"To'lov · #{str(payment.order_id)[:8]} · {payment.method.value}",
                occurred_at=payment.created_at,
                actor_user_id=user.id,
                related_payment_id=payment.id,
            )

    await db.commit()
    await db.refresh(payment)
    return PaymentOut.model_validate(payment)


@router.get("/summary/cash", response_model=DailyCashSummary)
async def daily_cash_summary(
    user: StaffAdmin,
    db: DbDep,
    day: date | None = Query(default=None, description="YYYY-MM-DD; default=today"),
    driver_id: UUID | None = Query(default=None),
) -> DailyCashSummary:
    tz = ZoneInfo(get_settings().APP_TIMEZONE)
    target = day or datetime.now(tz=tz).date()
    # Local midnight → UTC, and next local midnight → UTC
    day_start_utc = datetime.combine(target, time.min, tzinfo=tz).astimezone(timezone.utc)
    summary = await PaymentRepository(db).daily_cash_summary(
        user.company_id, day=day_start_utc, driver_id=driver_id
    )
    return DailyCashSummary(
        date=target,
        driver_id=driver_id,
        total_cash=summary["cash"],
        total_card_manual=summary["card_manual"],
        count=summary["count"],
    )


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(payment_id: UUID, user: CurrentUser, db: DbDep) -> PaymentOut:
    repo = PaymentRepository(db)
    payment = await repo.get(user.company_id, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentOut.model_validate(payment)


@router.post("/{payment_id}/refund", response_model=PaymentOut)
async def refund_payment(
    payment_id: UUID,
    payload: RefundRequest,
    user: StaffAdmin,
    db: DbDep,
) -> PaymentOut:
    service = PaymentService(db)
    payment = await service.payments.get(user.company_id, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment = await service.refund(
        user.company_id,
        payment,
        actor_user_id=user.id,
        reason=payload.reason,
    )
    await db.commit()
    await db.refresh(payment)
    return PaymentOut.model_validate(payment)
