from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, DbDep, require_roles
from app.models.user import User, UserRole
from app.repositories.bottle import BottleBalanceRepository
from app.repositories.driver import DriverRepository
from app.repositories.product import ProductRepository
from app.schemas.bottle import BottleAdjustRequest, BottleBalanceWithProduct
from app.services.bottle import BottleService

router = APIRouter(prefix="/drivers/{driver_id}/bottles", tags=["bottles"])

AdminOrOperator = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


@router.get("", response_model=list[BottleBalanceWithProduct])
async def get_driver_bottles(
    driver_id: UUID, user: CurrentUser, db: DbDep
) -> list[BottleBalanceWithProduct]:
    driver = await DriverRepository(db).get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    balances = await BottleBalanceRepository(db).list_for_driver(driver.id)
    result = []
    products_repo = ProductRepository(db)
    for b in balances:
        product = await products_repo.get(user.company_id, b.product_id)
        if product is None:
            continue
        result.append(
            BottleBalanceWithProduct(
                id=b.id,
                driver_id=b.driver_id,
                product_id=b.product_id,
                full_count=b.full_count,
                empty_count=b.empty_count,
                product_name=product.name,
                volume_liters=product.volume_liters,
            )
        )
    result.sort(key=lambda x: x.volume_liters, reverse=True)
    return result


@router.post("/adjust", response_model=BottleBalanceWithProduct)
async def adjust_driver_bottles(
    driver_id: UUID,
    payload: BottleAdjustRequest,
    user: AdminOrOperator,
    db: DbDep,
) -> BottleBalanceWithProduct:
    if payload.full_delta == 0 and payload.empty_delta == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide a non-zero delta",
        )
    driver = await DriverRepository(db).get(user.company_id, driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")

    service = BottleService(db)
    balance = await service.adjust_driver_balance(
        driver=driver,
        product_id=payload.product_id,
        full_delta=payload.full_delta,
        empty_delta=payload.empty_delta,
    )
    await db.commit()
    await db.refresh(balance)

    product = await ProductRepository(db).get(user.company_id, payload.product_id)
    assert product is not None
    return BottleBalanceWithProduct(
        id=balance.id,
        driver_id=balance.driver_id,
        product_id=balance.product_id,
        full_count=balance.full_count,
        empty_count=balance.empty_count,
        product_name=product.name,
        volume_liters=product.volume_liters,
    )
