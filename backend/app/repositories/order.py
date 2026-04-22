from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base(self, company_id: UUID):
        return select(Order).where(
            Order.company_id == company_id,
            Order.deleted_at.is_(None),
        )

    async def get(self, company_id: UUID, order_id: UUID) -> Order | None:
        stmt = self._base(company_id).where(Order.id == order_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_paginated(
        self,
        company_id: UUID,
        *,
        status: OrderStatus | None = None,
        driver_id: UUID | None = None,
        customer_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Order], int]:
        base = self._base(company_id)
        if status is not None:
            base = base.where(Order.status == status)
        if driver_id is not None:
            base = base.where(Order.driver_id == driver_id)
        if customer_id is not None:
            base = base.where(Order.customer_id == customer_id)
        if date_from is not None:
            base = base.where(Order.created_at >= date_from)
        if date_to is not None:
            base = base.where(Order.created_at <= date_to)

        total_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(total_stmt)).scalar_one()

        stmt = base.order_by(Order.created_at.desc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), int(total)

    async def add(self, order: Order) -> Order:
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
