from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbDep, require_roles
from app.models.bottle import DriverBottleBalance
from app.models.driver import Driver
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.warehouse import StockMovement, WarehouseStock
from app.schemas.warehouse import (
    StockMovementOut,
    WarehouseAdjust,
    WarehouseStockWithProduct,
    WarehouseSummary,
    WarehouseTransfer,
)

router = APIRouter(prefix="/warehouse", tags=["warehouse"])

StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


async def _get_or_create_stock(db, company_id: UUID, product_id: UUID) -> WarehouseStock:
    stock = (
        await db.execute(
            select(WarehouseStock).where(
                WarehouseStock.company_id == company_id,
                WarehouseStock.product_id == product_id,
            )
        )
    ).scalar_one_or_none()
    if stock is None:
        stock = WarehouseStock(
            company_id=company_id,
            product_id=product_id,
            full_count=0,
            empty_count=0,
        )
        db.add(stock)
        await db.flush()
    return stock


def _log(
    db,
    *,
    company_id: UUID,
    product_id: UUID,
    kind: str,
    full_delta: int = 0,
    empty_delta: int = 0,
    driver_id: UUID | None = None,
    reason: str | None = None,
    actor_user_id: UUID | None = None,
):
    db.add(
        StockMovement(
            company_id=company_id,
            product_id=product_id,
            kind=kind,
            full_delta=full_delta,
            empty_delta=empty_delta,
            driver_id=driver_id,
            reason=reason,
            actor_user_id=actor_user_id,
            occurred_at=datetime.now(tz=timezone.utc),
        )
    )


def _stock_out(stock: WarehouseStock, product: Product) -> WarehouseStockWithProduct:
    return WarehouseStockWithProduct(
        id=stock.id,
        product_id=product.id,
        product_name=product.name,
        volume_liters=product.volume_liters,
        is_returnable=product.is_returnable,
        full_count=stock.full_count,
        empty_count=stock.empty_count,
        updated_at=stock.updated_at,
    )


# ---------- READ ----------

@router.get("", response_model=list[WarehouseStockWithProduct])
async def list_warehouse(user: StaffUser, db: DbDep) -> list[WarehouseStockWithProduct]:
    """Stock per returnable product. Auto-creates 0-rows so admin can enter
    initial stock for any product."""
    products = (
        await db.execute(
            select(Product)
            .where(
                Product.company_id == user.company_id,
                Product.deleted_at.is_(None),
                Product.is_returnable.is_(True),
            )
            .order_by(Product.volume_liters.desc())
        )
    ).scalars().all()

    out: list[WarehouseStockWithProduct] = []
    for p in products:
        stock = await _get_or_create_stock(db, user.company_id, p.id)
        out.append(_stock_out(stock, p))
    await db.commit()
    return out


@router.get("/summary", response_model=list[WarehouseSummary])
async def warehouse_summary(user: StaffUser, db: DbDep) -> list[WarehouseSummary]:
    """Per-product reconciliation: warehouse + drivers."""
    products = (
        await db.execute(
            select(Product)
            .where(
                Product.company_id == user.company_id,
                Product.deleted_at.is_(None),
                Product.is_returnable.is_(True),
            )
            .order_by(Product.volume_liters.desc())
        )
    ).scalars().all()

    out: list[WarehouseSummary] = []
    for p in products:
        wh = (
            await db.execute(
                select(WarehouseStock).where(
                    WarehouseStock.company_id == user.company_id,
                    WarehouseStock.product_id == p.id,
                )
            )
        ).scalar_one_or_none()
        wh_full = wh.full_count if wh else 0
        wh_empty = wh.empty_count if wh else 0

        drv_row = (
            await db.execute(
                select(
                    func.coalesce(func.sum(DriverBottleBalance.full_count), 0),
                    func.coalesce(func.sum(DriverBottleBalance.empty_count), 0),
                )
                .select_from(DriverBottleBalance)
                .join(Driver, Driver.id == DriverBottleBalance.driver_id)
                .where(
                    Driver.company_id == user.company_id,
                    Driver.deleted_at.is_(None),
                    DriverBottleBalance.product_id == p.id,
                )
            )
        ).one()
        drv_full = int(drv_row[0] or 0)
        drv_empty = int(drv_row[1] or 0)

        # Per-product customer debt requires schema change; v1 reports 0 here.
        customer_debt = 0

        out.append(
            WarehouseSummary(
                product_id=p.id,
                product_name=p.name,
                volume_liters=p.volume_liters,
                warehouse_full=wh_full,
                warehouse_empty=wh_empty,
                drivers_full=drv_full,
                drivers_empty=drv_empty,
                customer_debt=customer_debt,
                total_in_system=wh_full + wh_empty + drv_full + drv_empty + customer_debt,
            )
        )
    return out


@router.get("/movements", response_model=list[StockMovementOut])
async def list_movements(user: StaffUser, db: DbDep) -> list[StockMovementOut]:
    rows = (
        await db.execute(
            select(StockMovement)
            .where(StockMovement.company_id == user.company_id)
            .order_by(StockMovement.occurred_at.desc())
            .limit(200)
        )
    ).scalars().all()
    return [StockMovementOut.model_validate(r) for r in rows]


# ---------- WRITE ----------

@router.post("/adjust", response_model=WarehouseStockWithProduct)
async def adjust_warehouse(
    payload: WarehouseAdjust, user: StaffUser, db: DbDep
) -> WarehouseStockWithProduct:
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

    stock = await _get_or_create_stock(db, user.company_id, product.id)
    new_full = stock.full_count + payload.full_delta
    new_empty = stock.empty_count + payload.empty_delta
    if new_full < 0 or new_empty < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Ombor balansi manfiy bo'lib qoladi. "
                f"Joriy: to'la {stock.full_count}, bo'sh {stock.empty_count}"
            ),
        )
    stock.full_count = new_full
    stock.empty_count = new_empty

    _log(
        db,
        company_id=user.company_id,
        product_id=product.id,
        kind="manual",
        full_delta=payload.full_delta,
        empty_delta=payload.empty_delta,
        reason=payload.reason,
        actor_user_id=user.id,
    )

    await db.commit()
    await db.refresh(stock)
    return _stock_out(stock, product)


@router.post("/transfer/to-driver", response_model=WarehouseStockWithProduct)
async def transfer_to_driver(
    payload: WarehouseTransfer, user: StaffUser, db: DbDep
) -> WarehouseStockWithProduct:
    if payload.full_count == 0 and payload.empty_count == 0:
        raise HTTPException(status_code=422, detail="Hech narsa kiritilmagan")

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

    driver = (
        await db.execute(
            select(Driver).where(
                Driver.id == payload.driver_id,
                Driver.company_id == user.company_id,
                Driver.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if driver is None:
        raise HTTPException(status_code=404, detail="Haydovchi topilmadi")

    stock = await _get_or_create_stock(db, user.company_id, product.id)
    if stock.full_count < payload.full_count or stock.empty_count < payload.empty_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Omborda yetarli emas. To'la: {stock.full_count}, "
                f"bo'sh: {stock.empty_count}"
            ),
        )

    drv_balance = (
        await db.execute(
            select(DriverBottleBalance).where(
                DriverBottleBalance.driver_id == driver.id,
                DriverBottleBalance.product_id == product.id,
            )
        )
    ).scalar_one_or_none()
    if drv_balance is None:
        drv_balance = DriverBottleBalance(
            driver_id=driver.id,
            product_id=product.id,
            full_count=0,
            empty_count=0,
        )
        db.add(drv_balance)
        await db.flush()

    stock.full_count -= payload.full_count
    stock.empty_count -= payload.empty_count
    drv_balance.full_count += payload.full_count
    drv_balance.empty_count += payload.empty_count

    _log(
        db,
        company_id=user.company_id,
        product_id=product.id,
        kind="load_driver",
        full_delta=-payload.full_count,
        empty_delta=-payload.empty_count,
        driver_id=driver.id,
        reason=payload.reason,
        actor_user_id=user.id,
    )

    await db.commit()
    await db.refresh(stock)
    return _stock_out(stock, product)


@router.post("/transfer/from-driver", response_model=WarehouseStockWithProduct)
async def transfer_from_driver(
    payload: WarehouseTransfer, user: StaffUser, db: DbDep
) -> WarehouseStockWithProduct:
    if payload.full_count == 0 and payload.empty_count == 0:
        raise HTTPException(status_code=422, detail="Hech narsa kiritilmagan")

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

    driver = (
        await db.execute(
            select(Driver).where(
                Driver.id == payload.driver_id,
                Driver.company_id == user.company_id,
                Driver.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if driver is None:
        raise HTTPException(status_code=404, detail="Haydovchi topilmadi")

    drv_balance = (
        await db.execute(
            select(DriverBottleBalance).where(
                DriverBottleBalance.driver_id == driver.id,
                DriverBottleBalance.product_id == product.id,
            )
        )
    ).scalar_one_or_none()
    if drv_balance is None or (
        drv_balance.full_count < payload.full_count
        or drv_balance.empty_count < payload.empty_count
    ):
        cur_full = drv_balance.full_count if drv_balance else 0
        cur_empty = drv_balance.empty_count if drv_balance else 0
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(f"Haydovchida yetarli emas. To'la: {cur_full}, bo'sh: {cur_empty}"),
        )

    stock = await _get_or_create_stock(db, user.company_id, product.id)
    drv_balance.full_count -= payload.full_count
    drv_balance.empty_count -= payload.empty_count
    stock.full_count += payload.full_count
    stock.empty_count += payload.empty_count

    _log(
        db,
        company_id=user.company_id,
        product_id=product.id,
        kind="return_driver",
        full_delta=+payload.full_count,
        empty_delta=+payload.empty_count,
        driver_id=driver.id,
        reason=payload.reason,
        actor_user_id=user.id,
    )

    await db.commit()
    await db.refresh(stock)
    return _stock_out(stock, product)
