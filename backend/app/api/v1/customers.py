from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_roles
from app.models.user import User, UserRole
from app.schemas.address import AddressCreate, AddressOut, AddressUpdate
from app.schemas.common import OkResponse
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.schemas.pagination import Page, PageParams
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.OPERATOR)),
]


@router.get("", response_model=Page[CustomerOut])
async def list_customers(
    user: StaffUser,
    db: DbDep,
    q: str | None = Query(default=None, description="phone or name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[CustomerOut]:
    params = PageParams(page=page, page_size=page_size)
    service = CustomerService(db)
    items, total = await service.customers.list_paginated(
        user.company_id,
        query=q,
        offset=params.offset,
        limit=params.limit,
    )
    return Page[CustomerOut](
        items=[CustomerOut.model_validate(c) for c in items],
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    user: StaffUser,
    db: DbDep,
) -> CustomerOut:
    service = CustomerService(db)
    customer = await service.create_customer(user.company_id, payload)
    await db.commit()
    await db.refresh(customer)
    return CustomerOut.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: UUID, user: StaffUser, db: DbDep) -> CustomerOut:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerOut.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    user: StaffUser,
    db: DbDep,
) -> CustomerOut:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer = await service.update_customer(customer, payload)
    await db.commit()
    return CustomerOut.model_validate(customer)


@router.delete("/{customer_id}", response_model=OkResponse)
async def delete_customer(customer_id: UUID, user: StaffUser, db: DbDep) -> OkResponse:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    await service.customers.delete(customer)
    await db.commit()
    return OkResponse()


# ---- Addresses ----

@router.get("/{customer_id}/addresses", response_model=list[AddressOut])
async def list_addresses(
    customer_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> list[AddressOut]:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    addresses = await service.addresses.list_for_customer(customer.id)
    return [AddressOut.model_validate(a) for a in addresses]


@router.post(
    "/{customer_id}/addresses",
    response_model=AddressOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    customer_id: UUID,
    payload: AddressCreate,
    user: StaffUser,
    db: DbDep,
) -> AddressOut:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    address = await service.add_address(customer, payload)
    await db.commit()
    await db.refresh(address)
    return AddressOut.model_validate(address)


@router.get("/{customer_id}/addresses/{address_id}", response_model=AddressOut)
async def get_address(
    customer_id: UUID,
    address_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> AddressOut:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    address = await service.addresses.get(customer.id, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return AddressOut.model_validate(address)


@router.patch("/{customer_id}/addresses/{address_id}", response_model=AddressOut)
async def update_address(
    customer_id: UUID,
    address_id: UUID,
    payload: AddressUpdate,
    user: StaffUser,
    db: DbDep,
) -> AddressOut:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    address = await service.addresses.get(customer.id, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    address = await service.update_address(address, payload)
    await db.commit()
    return AddressOut.model_validate(address)


@router.delete("/{customer_id}/addresses/{address_id}", response_model=OkResponse)
async def delete_address(
    customer_id: UUID,
    address_id: UUID,
    user: StaffUser,
    db: DbDep,
) -> OkResponse:
    service = CustomerService(db)
    customer = await service.customers.get(user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    address = await service.addresses.get(customer.id, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    await service.addresses.delete(address)
    await db.commit()
    return OkResponse()
