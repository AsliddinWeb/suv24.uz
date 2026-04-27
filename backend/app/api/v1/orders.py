from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import CurrentUser, DbDep, require_roles
from app.core.tariff import EnforceOrders
from app.models.driver import Driver
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.repositories.payment import PaymentRepository
from app.schemas.bottle import DeliverRequest
from app.schemas.order import (
    AssignDriverRequest,
    OrderCreate,
    OrderDetailOut,
    OrderOut,
    OrderUpdate,
    ReasonRequest,
)
from app.schemas.pagination import Page, PageParams
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


async def _load_driver_for_order(service: OrderService, user: User) -> Driver:
    driver = await service.drivers.get_by_user_id(user.company_id, user.id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found for this user",
        )
    return driver


async def _with_paid_amount(db, orders: list[Order]) -> list[Order]:
    if not orders:
        return orders
    from app.repositories.address import AddressRepository
    from app.repositories.customer import CustomerRepository
    from sqlalchemy import select
    from app.models.customer import Customer, CustomerAddress

    paid_map = await PaymentRepository(db).paid_sums_for_orders([o.id for o in orders])

    # Batch fetch customers and addresses
    customer_ids = list({o.customer_id for o in orders})
    address_ids = list({o.address_id for o in orders})

    customer_rows = (
        await db.execute(select(Customer).where(Customer.id.in_(customer_ids)))
    ).scalars().all()
    address_rows = (
        await db.execute(select(CustomerAddress).where(CustomerAddress.id.in_(address_ids)))
    ).scalars().all()

    cust_map = {c.id: c for c in customer_rows}
    addr_map = {a.id: a for a in address_rows}

    for o in orders:
        o.paid_amount = paid_map.get(o.id, Decimal("0"))
        o.customer = cust_map.get(o.customer_id)  # type: ignore[attr-defined]
        o.address = addr_map.get(o.address_id)  # type: ignore[attr-defined]
    return orders


async def _single_with_paid(db, order: Order) -> Order:
    paid = await PaymentRepository(db).total_paid_for_order(order.id)
    order.paid_amount = paid
    return order


async def _detail_out(db, order: Order) -> OrderDetailOut:
    await _single_with_paid(db, order)
    # Attach customer + address for nested serialization
    from app.repositories.address import AddressRepository
    from app.repositories.customer import CustomerRepository

    customer = await CustomerRepository(db).get(order.company_id, order.customer_id)
    address = await AddressRepository(db).get(order.customer_id, order.address_id)
    order.customer = customer  # type: ignore[attr-defined]
    order.address = address  # type: ignore[attr-defined]
    return OrderDetailOut.model_validate(order)


@router.get("", response_model=Page[OrderOut])
async def list_orders(
    user: CurrentUser,
    db: DbDep,
    order_status: OrderStatus | None = Query(default=None, alias="status"),
    driver_id: UUID | None = Query(default=None),
    customer_id: UUID | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[OrderOut]:
    service = OrderService(db)
    effective_driver_id = driver_id
    if user.role == UserRole.DRIVER:
        driver = await _load_driver_for_order(service, user)
        effective_driver_id = driver.id

    params = PageParams(page=page, page_size=page_size)
    items, total = await service.orders.list_paginated(
        user.company_id,
        status=order_status,
        driver_id=effective_driver_id,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
        offset=params.offset,
        limit=params.limit,
    )
    await _with_paid_amount(db, items)
    return Page[OrderOut](
        items=[OrderOut.model_validate(o) for o in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("", response_model=OrderDetailOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    user: StaffUser,
    db: DbDep,
    _: EnforceOrders = None,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.create_order(
        company_id=user.company_id,
        actor_user_id=user.id,
        data=payload,
    )
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


async def _load_order_for_user(service: OrderService, user: User, order_id: UUID):
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if user.role == UserRole.DRIVER:
        driver = await _load_driver_for_order(service, user)
        if order.driver_id != driver.id:
            raise HTTPException(status_code=403, detail="Not your order")
    return order


@router.get("/{order_id}", response_model=OrderDetailOut)
async def get_order(order_id: UUID, user: CurrentUser, db: DbDep) -> OrderDetailOut:
    service = OrderService(db)
    order = await _load_order_for_user(service, user, order_id)
    return await _detail_out(db, order)


@router.patch("/{order_id}", response_model=OrderDetailOut)
async def update_order(
    order_id: UUID,
    payload: OrderUpdate,
    user: StaffUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.is_terminal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update a terminal order",
        )
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(order, field, value)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.delete("/{order_id}")
async def delete_order(
    order_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> dict[str, bool]:
    from sqlalchemy import func as sql_func

    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.deleted_at = sql_func.now()  # type: ignore[assignment]
    await db.commit()
    return {"ok": True}


@router.post("/{order_id}/assign", response_model=OrderDetailOut)
async def assign_driver(
    order_id: UUID,
    payload: AssignDriverRequest,
    user: StaffUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    driver = await service.drivers.get(user.company_id, payload.driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    order = await service.assign_driver(order, driver, actor_user_id=user.id)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/unassign", response_model=OrderDetailOut)
async def unassign_driver(
    order_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order = await service.unassign_driver(order, actor_user_id=user.id)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/start", response_model=OrderDetailOut)
async def start_delivery(
    order_id: UUID,
    user: CurrentUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await _load_order_for_user(service, user, order_id)
    order = await service.start_delivery(order, actor_user_id=user.id)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/deliver", response_model=OrderDetailOut)
async def mark_delivered(
    order_id: UUID,
    user: CurrentUser,
    db: DbDep,
    payload: DeliverRequest | None = None,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await _load_order_for_user(service, user, order_id)
    returns_map: dict[UUID, int] = {}
    if payload is not None:
        for ret in payload.bottle_returns:
            returns_map[ret.product_id] = returns_map.get(ret.product_id, 0) + ret.count
    order = await service.mark_delivered(
        order, actor_user_id=user.id, bottle_returns=returns_map
    )
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/fail", response_model=OrderDetailOut)
async def mark_failed(
    order_id: UUID,
    payload: ReasonRequest,
    user: CurrentUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await _load_order_for_user(service, user, order_id)
    order = await service.mark_failed(order, actor_user_id=user.id, reason=payload.reason)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/cancel", response_model=OrderDetailOut)
async def cancel_order(
    order_id: UUID,
    payload: ReasonRequest,
    user: StaffUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order = await service.cancel(order, actor_user_id=user.id, reason=payload.reason)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)


@router.post("/{order_id}/retry", response_model=OrderDetailOut)
async def retry_order(
    order_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> OrderDetailOut:
    service = OrderService(db)
    order = await service.orders.get(user.company_id, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order = await service.retry(order, actor_user_id=user.id)
    await db.commit()
    await db.refresh(order)
    return await _detail_out(db, order)
