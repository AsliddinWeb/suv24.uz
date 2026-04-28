from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import case, func, select

from app.core.config import get_settings
from app.core.deps import DbDep, require_roles
from app.models.cash import (
    CashAccount,
    CashTransaction,
    CashTransactionKind,
    InventoryPurchase,
)
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.warehouse import StockMovement, WarehouseStock
from app.schemas.cash import (
    CashAccountOut,
    CashSnapshot,
    CashTransactionOut,
    ExpenseIn,
    ManualCashIn,
    OpeningBalanceIn,
    PurchaseIn,
    PurchaseOut,
)

router = APIRouter(prefix="/warehouse/cash", tags=["cash"])
purchase_router = APIRouter(prefix="/warehouse/purchases", tags=["cash"])

StaffAdmin = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
]
StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


# ----- helpers -----

async def _get_or_create_account(db, company_id: UUID) -> CashAccount:
    acc = (
        await db.execute(select(CashAccount).where(CashAccount.company_id == company_id))
    ).scalar_one_or_none()
    if acc is None:
        acc = CashAccount(company_id=company_id, balance=Decimal("0.00"), currency="UZS")
        db.add(acc)
        await db.flush()
    return acc


def _record(
    db,
    *,
    account: CashAccount,
    kind: CashTransactionKind,
    amount: Decimal,
    description: str | None,
    occurred_at: datetime | None,
    actor_user_id: UUID | None,
    related_purchase_id: UUID | None = None,
    related_payment_id: UUID | None = None,
) -> CashTransaction:
    """Append a transaction and update the running balance."""
    tx = CashTransaction(
        company_id=account.company_id,
        kind=kind,
        amount=amount,
        description=description,
        occurred_at=occurred_at or datetime.now(tz=timezone.utc),
        actor_user_id=actor_user_id,
        related_purchase_id=related_purchase_id,
        related_payment_id=related_payment_id,
    )
    db.add(tx)
    account.balance = (account.balance or Decimal("0")) + amount
    return tx


# ----- READ -----

@router.get("", response_model=CashSnapshot)
async def get_cash_snapshot(user: StaffUser, db: DbDep) -> CashSnapshot:
    acc = await _get_or_create_account(db, user.company_id)
    recent_rows = (
        await db.execute(
            select(CashTransaction)
            .where(CashTransaction.company_id == user.company_id)
            .order_by(CashTransaction.occurred_at.desc())
            .limit(10)
        )
    ).scalars().all()
    snapshot = CashSnapshot(
        account=CashAccountOut.model_validate(acc),
        recent=[CashTransactionOut.model_validate(r) for r in recent_rows],
        needs_opening_balance=acc.opening_set_at is None,
    )
    await db.commit()
    return snapshot


class CashSummary(BaseModel):
    balance: Decimal
    today_in: Decimal
    today_out: Decimal
    month_in: Decimal
    month_out: Decimal


@router.get("/summary", response_model=CashSummary)
async def cash_summary(user: StaffUser, db: DbDep) -> CashSummary:
    """Today / month money-in / money-out for the dashboard header."""
    acc = await _get_or_create_account(db, user.company_id)

    tz = ZoneInfo(get_settings().APP_TIMEZONE)
    now_local = datetime.now(tz=tz)
    today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    month_local = today_local.replace(day=1)
    today_utc = today_local.astimezone(timezone.utc)
    month_utc = month_local.astimezone(timezone.utc)

    money_in = func.coalesce(
        func.sum(case((CashTransaction.amount > 0, CashTransaction.amount), else_=0)), 0
    )
    money_out = func.coalesce(
        func.sum(case((CashTransaction.amount < 0, -CashTransaction.amount), else_=0)), 0
    )

    today_row = (
        await db.execute(
            select(money_in, money_out).where(
                CashTransaction.company_id == user.company_id,
                CashTransaction.occurred_at >= today_utc,
            )
        )
    ).one()
    month_row = (
        await db.execute(
            select(money_in, money_out).where(
                CashTransaction.company_id == user.company_id,
                CashTransaction.occurred_at >= month_utc,
            )
        )
    ).one()

    await db.commit()
    return CashSummary(
        balance=acc.balance,
        today_in=Decimal(today_row[0] or 0),
        today_out=Decimal(today_row[1] or 0),
        month_in=Decimal(month_row[0] or 0),
        month_out=Decimal(month_row[1] or 0),
    )


@router.get("/transactions", response_model=list[CashTransactionOut])
async def list_transactions(
    user: StaffUser,
    db: DbDep,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CashTransactionOut]:
    rows = (
        await db.execute(
            select(CashTransaction)
            .where(CashTransaction.company_id == user.company_id)
            .order_by(CashTransaction.occurred_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [CashTransactionOut.model_validate(r) for r in rows]


# ----- WRITE -----

@router.post("/opening-balance", response_model=CashAccountOut)
async def set_opening_balance(
    payload: OpeningBalanceIn, user: StaffAdmin, db: DbDep
) -> CashAccountOut:
    acc = await _get_or_create_account(db, user.company_id)
    if acc.opening_set_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Boshlang'ich balans allaqachon kiritilgan. "
                "Tuzatish kerak bo'lsa qo'lda kirim/chiqim qiling."
            ),
        )
    if payload.amount > 0:
        _record(
            db,
            account=acc,
            kind=CashTransactionKind.OPENING_BALANCE,
            amount=payload.amount,
            description=payload.note or "Boshlang'ich balans",
            occurred_at=datetime.now(tz=timezone.utc),
            actor_user_id=user.id,
        )
    acc.opening_set_at = datetime.now(tz=timezone.utc)
    await db.commit()
    await db.refresh(acc)
    return CashAccountOut.model_validate(acc)


@router.post("/expense", response_model=CashTransactionOut)
async def record_expense(
    payload: ExpenseIn, user: StaffAdmin, db: DbDep
) -> CashTransactionOut:
    acc = await _get_or_create_account(db, user.company_id)
    tx = _record(
        db,
        account=acc,
        kind=CashTransactionKind.EXPENSE,
        amount=-payload.amount,
        description=payload.description,
        occurred_at=payload.occurred_at,
        actor_user_id=user.id,
    )
    await db.commit()
    await db.refresh(tx)
    return CashTransactionOut.model_validate(tx)


@router.post("/manual", response_model=CashTransactionOut)
async def record_manual(
    payload: ManualCashIn, user: StaffAdmin, db: DbDep
) -> CashTransactionOut:
    acc = await _get_or_create_account(db, user.company_id)
    if payload.direction == "in":
        kind = CashTransactionKind.MANUAL_IN
        amount = payload.amount
    else:
        kind = CashTransactionKind.MANUAL_OUT
        amount = -payload.amount
    tx = _record(
        db,
        account=acc,
        kind=kind,
        amount=amount,
        description=payload.description,
        occurred_at=payload.occurred_at,
        actor_user_id=user.id,
    )
    await db.commit()
    await db.refresh(tx)
    return CashTransactionOut.model_validate(tx)


# ----- Inventory purchases (warehouse goods receipt) -----


@purchase_router.get("", response_model=list[PurchaseOut])
async def list_purchases(
    user: StaffUser, db: DbDep, limit: int = Query(default=100, ge=1, le=500)
) -> list[PurchaseOut]:
    rows = (
        await db.execute(
            select(InventoryPurchase, Product.name, Product.volume_liters)
            .join(Product, Product.id == InventoryPurchase.product_id)
            .where(InventoryPurchase.company_id == user.company_id)
            .order_by(InventoryPurchase.occurred_at.desc())
            .limit(limit)
        )
    ).all()
    out: list[PurchaseOut] = []
    for purchase, name, volume in rows:
        d = PurchaseOut.model_validate(purchase).model_dump()
        d["product_name"] = name
        d["volume_liters"] = volume
        out.append(PurchaseOut(**d))
    return out


@purchase_router.post("", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
async def record_purchase(
    payload: PurchaseIn, user: StaffAdmin, db: DbDep
) -> PurchaseOut:
    """Record a warehouse goods receipt: products IN, cash OUT (atomic)."""
    if payload.full_count == 0 and payload.empty_count == 0:
        raise HTTPException(status_code=422, detail="Soni 0 bo'lmasin")

    product = (
        await db.execute(
            select(Product).where(
                Product.id == payload.product_id,
                Product.company_id == user.company_id,
                Product.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    if not product.is_returnable:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mahsulot qaytariladigan emas",
        )

    qty_total = payload.full_count + payload.empty_count
    total_cost = (payload.unit_cost * qty_total).quantize(Decimal("0.01"))
    occurred_at = payload.occurred_at or datetime.now(tz=timezone.utc)

    purchase = InventoryPurchase(
        company_id=user.company_id,
        product_id=product.id,
        full_count=payload.full_count,
        empty_count=payload.empty_count,
        unit_cost=payload.unit_cost,
        total_cost=total_cost,
        supplier=payload.supplier,
        note=payload.note,
        occurred_at=occurred_at,
        actor_user_id=user.id,
    )
    db.add(purchase)
    await db.flush()

    # Warehouse stock update
    stock = (
        await db.execute(
            select(WarehouseStock).where(
                WarehouseStock.company_id == user.company_id,
                WarehouseStock.product_id == product.id,
            )
        )
    ).scalar_one_or_none()
    if stock is None:
        stock = WarehouseStock(
            company_id=user.company_id,
            product_id=product.id,
            full_count=0,
            empty_count=0,
        )
        db.add(stock)
        await db.flush()
    stock.full_count += payload.full_count
    stock.empty_count += payload.empty_count

    # Stock movement audit
    db.add(
        StockMovement(
            company_id=user.company_id,
            product_id=product.id,
            kind="purchase",
            full_delta=+payload.full_count,
            empty_delta=+payload.empty_count,
            reason=payload.supplier or payload.note,
            actor_user_id=user.id,
            occurred_at=occurred_at,
        )
    )

    # Cash OUT
    if total_cost > 0:
        acc = await _get_or_create_account(db, user.company_id)
        _record(
            db,
            account=acc,
            kind=CashTransactionKind.PURCHASE,
            amount=-total_cost,
            description=(
                f"{product.name} {product.volume_liters}L · "
                f"{payload.full_count} to'la + {payload.empty_count} bo'sh"
                + (f" · {payload.supplier}" if payload.supplier else "")
            ),
            occurred_at=occurred_at,
            actor_user_id=user.id,
            related_purchase_id=purchase.id,
        )

    await db.commit()
    await db.refresh(purchase)
    out = PurchaseOut.model_validate(purchase).model_dump()
    out["product_name"] = product.name
    out["volume_liters"] = product.volume_liters
    return PurchaseOut(**out)
