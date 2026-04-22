from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import CustomerAddress


class AddressRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_customer(self, customer_id: UUID) -> list[CustomerAddress]:
        stmt = (
            select(CustomerAddress)
            .where(
                CustomerAddress.customer_id == customer_id,
                CustomerAddress.deleted_at.is_(None),
            )
            .order_by(CustomerAddress.created_at.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get(self, customer_id: UUID, address_id: UUID) -> CustomerAddress | None:
        stmt = select(CustomerAddress).where(
            CustomerAddress.id == address_id,
            CustomerAddress.customer_id == customer_id,
            CustomerAddress.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_qr_token(self, qr_token: str) -> CustomerAddress | None:
        stmt = select(CustomerAddress).where(
            CustomerAddress.qr_token == qr_token,
            CustomerAddress.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create(self, address: CustomerAddress) -> CustomerAddress:
        self.db.add(address)
        await self.db.flush()
        await self.db.refresh(address)
        return address

    async def delete(self, address: CustomerAddress) -> None:
        address.deleted_at = func.now()  # type: ignore[assignment]
        await self.db.flush()
