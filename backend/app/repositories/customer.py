from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base(self, company_id: UUID):
        return select(Customer).where(
            Customer.company_id == company_id,
            Customer.deleted_at.is_(None),
        )

    async def get(self, company_id: UUID, customer_id: UUID) -> Customer | None:
        stmt = self._base(company_id).where(Customer.id == customer_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_phone(self, company_id: UUID, phone: str) -> Customer | None:
        stmt = self._base(company_id).where(Customer.phone == phone)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_paginated(
        self,
        company_id: UUID,
        *,
        query: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Customer], int]:
        base = self._base(company_id)
        if query:
            like = f"%{query}%"
            base = base.where(or_(Customer.full_name.ilike(like), Customer.phone.ilike(like)))

        total_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(total_stmt)).scalar_one()

        stmt = base.order_by(Customer.created_at.desc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), int(total)

    async def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(customer)
        return customer

    async def delete(self, customer: Customer) -> None:
        customer.deleted_at = func.now()  # type: ignore[assignment]
        await self.db.flush()
