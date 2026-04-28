from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbDep, require_roles
from app.models.bottle import DriverBottleBalance
from app.models.driver import Driver
from app.models.user import User, UserRole
from app.models.warehouse import WarehouseStock
from app.schemas.common import OkResponse
from app.schemas.product import PriceCreate, PriceOut, ProductCreate, ProductOut, ProductUpdate
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


class ProductStockSummary(BaseModel):
    product_id: UUID
    warehouse_full: int
    warehouse_empty: int
    drivers_full: int
    drivers_empty: int
    available_full: int  # warehouse_full + drivers_full — what we can still deliver
    is_returnable: bool

AdminUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
]


async def _to_out(service: ProductService, product) -> ProductOut:
    price = await service.current_price(product)
    return ProductOut(
        id=product.id,
        company_id=product.company_id,
        name=product.name,
        volume_liters=product.volume_liters,
        is_returnable=product.is_returnable,
        is_active=product.is_active,
        current_price=price,
    )


@router.get("", response_model=list[ProductOut])
async def list_products(
    user: CurrentUser,
    db: DbDep,
    only_active: bool = Query(default=False),
) -> list[ProductOut]:
    service = ProductService(db)
    items = await service.products.list_all(user.company_id, only_active=only_active)
    return [await _to_out(service, p) for p in items]


@router.get("/stocks", response_model=list[ProductStockSummary])
async def list_product_stocks(
    user: CurrentUser, db: DbDep
) -> list[ProductStockSummary]:
    """Per-product live inventory across warehouse and all drivers."""
    service = ProductService(db)
    products = await service.products.list_all(user.company_id, only_active=False)
    out: list[ProductStockSummary] = []
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
        drv = (
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
        drv_full = int(drv[0] or 0)
        drv_empty = int(drv[1] or 0)
        out.append(
            ProductStockSummary(
                product_id=p.id,
                warehouse_full=wh_full,
                warehouse_empty=wh_empty,
                drivers_full=drv_full,
                drivers_empty=drv_empty,
                available_full=wh_full + drv_full,
                is_returnable=p.is_returnable,
            )
        )
    return out


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, user: CurrentUser, db: DbDep) -> ProductOut:
    service = ProductService(db)
    product = await service.products.get(user.company_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return await _to_out(service, product)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    user: AdminUser,
    db: DbDep,
) -> ProductOut:
    service = ProductService(db)
    product = await service.create_product(user.company_id, payload)
    await db.commit()
    await db.refresh(product)
    return await _to_out(service, product)


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    user: AdminUser,
    db: DbDep,
) -> ProductOut:
    service = ProductService(db)
    product = await service.products.get(user.company_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product = await service.update_product(product, payload)
    await db.commit()
    return await _to_out(service, product)


@router.delete("/{product_id}", response_model=OkResponse)
async def delete_product(
    product_id: UUID,
    user: AdminUser,
    db: DbDep,
) -> OkResponse:
    service = ProductService(db)
    product = await service.products.get(user.company_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await service.products.delete(product)
    await db.commit()
    return OkResponse()


@router.get("/{product_id}/prices", response_model=list[PriceOut])
async def list_prices(
    product_id: UUID,
    user: CurrentUser,
    db: DbDep,
) -> list[PriceOut]:
    service = ProductService(db)
    product = await service.products.get(user.company_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    history = await service.prices.list_history(product.id)
    return [PriceOut.model_validate(p) for p in history]


@router.post(
    "/{product_id}/prices",
    response_model=PriceOut,
    status_code=status.HTTP_201_CREATED,
)
async def set_price(
    product_id: UUID,
    payload: PriceCreate,
    user: AdminUser,
    db: DbDep,
) -> PriceOut:
    service = ProductService(db)
    product = await service.products.get(user.company_id, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    price = await service.set_price(product, payload.price)
    await db.commit()
    await db.refresh(price)
    return PriceOut.model_validate(price)
