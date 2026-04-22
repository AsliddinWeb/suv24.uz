import secrets
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerAddress
from app.repositories.address import AddressRepository
from app.repositories.customer import CustomerRepository
from app.schemas.address import AddressCreate, AddressUpdate
from app.schemas.customer import CustomerCreate, CustomerUpdate


QR_TOKEN_BYTES = 8  # ~11 URL-safe chars


def generate_qr_token() -> str:
    return secrets.token_urlsafe(QR_TOKEN_BYTES)


class CustomerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.customers = CustomerRepository(db)
        self.addresses = AddressRepository(db)

    async def create_customer(self, company_id: UUID, data: CustomerCreate) -> Customer:
        existing = await self.customers.get_by_phone(company_id, data.phone)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer with this phone already exists",
            )
        customer = Customer(
            company_id=company_id,
            phone=data.phone,
            full_name=data.full_name,
            segment=data.segment,
            notes=data.notes,
        )
        return await self.customers.create(customer)

    async def update_customer(self, customer: Customer, data: CustomerUpdate) -> Customer:
        changed = data.model_dump(exclude_unset=True)
        for field, value in changed.items():
            setattr(customer, field, value)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already in use",
            ) from exc
        await self.db.refresh(customer)
        return customer

    async def add_address(
        self,
        customer: Customer,
        data: AddressCreate,
    ) -> CustomerAddress:
        for _ in range(5):
            token = generate_qr_token()
            if await self.addresses.get_by_qr_token(token) is None:
                break
        else:  # pragma: no cover
            raise HTTPException(status_code=500, detail="Failed to generate QR token")

        address = CustomerAddress(
            customer_id=customer.id,
            label=data.label,
            address_text=data.address_text,
            lat=data.lat,
            lng=data.lng,
            notes=data.notes,
            qr_token=token,
            is_active=True,
        )
        return await self.addresses.create(address)

    async def update_address(
        self,
        address: CustomerAddress,
        data: AddressUpdate,
    ) -> CustomerAddress:
        changed = data.model_dump(exclude_unset=True)
        for field, value in changed.items():
            setattr(address, field, value)
        await self.db.flush()
        await self.db.refresh(address)
        return address
