from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment, PaymentMethod, PaymentStatus


class PaymentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base(self, company_id: UUID):
        return select(Payment).where(
            Payment.company_id == company_id,
            Payment.deleted_at.is_(None),
        )

    async def get(self, company_id: UUID, payment_id: UUID) -> Payment | None:
        stmt = self._base(company_id).where(Payment.id == payment_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_paginated(
        self,
        company_id: UUID,
        *,
        order_id: UUID | None = None,
        customer_id: UUID | None = None,
        method: PaymentMethod | None = None,
        payment_status: PaymentStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Payment], int]:
        base = self._base(company_id)
        if order_id is not None:
            base = base.where(Payment.order_id == order_id)
        if customer_id is not None:
            base = base.where(Payment.customer_id == customer_id)
        if method is not None:
            base = base.where(Payment.method == method)
        if payment_status is not None:
            base = base.where(Payment.status == payment_status)
        if date_from is not None:
            base = base.where(Payment.created_at >= date_from)
        if date_to is not None:
            base = base.where(Payment.created_at <= date_to)

        total_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(total_stmt)).scalar_one()

        stmt = base.order_by(Payment.created_at.desc()).offset(offset).limit(limit)
        rows = (await self.db.execute(stmt)).scalars().all()
        return list(rows), int(total)

    async def total_paid_for_order(self, order_id: UUID) -> Decimal:
        stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.order_id == order_id,
            Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
            Payment.deleted_at.is_(None),
        )
        val = (await self.db.execute(stmt)).scalar_one()
        return Decimal(val)

    async def paid_sums_for_orders(self, order_ids: list[UUID]) -> dict[UUID, Decimal]:
        if not order_ids:
            return {}
        stmt = (
            select(
                Payment.order_id,
                func.coalesce(func.sum(Payment.amount), 0).label("paid"),
            )
            .where(
                Payment.order_id.in_(order_ids),
                Payment.status.in_([PaymentStatus.PAID, PaymentStatus.PARTIAL]),
                Payment.deleted_at.is_(None),
            )
            .group_by(Payment.order_id)
        )
        rows = (await self.db.execute(stmt)).all()
        return {row.order_id: Decimal(row.paid) for row in rows}

    async def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def daily_cash_summary(
        self,
        company_id: UUID,
        *,
        day: datetime,
        driver_id: UUID | None = None,
    ) -> dict:
        from app.models.order import Order
        from sqlalchemy import and_

        # `day` is already the local day's midnight translated to UTC.
        # Upper bound = next local midnight translated to UTC (via 24h span
        # which is correct since Asia/Tashkent has no DST).
        day_start = day
        day_end = day_start + timedelta(days=1)

        conditions = [
            Payment.company_id == company_id,
            Payment.status == PaymentStatus.PAID,
            Payment.deleted_at.is_(None),
            Payment.created_at >= day_start,
            Payment.created_at < day_end,
        ]
        stmt = select(
            Payment.method,
            func.coalesce(func.sum(Payment.amount), 0).label("total"),
            func.count().label("cnt"),
        ).where(and_(*conditions))

        if driver_id is not None:
            stmt = stmt.join(Order, Order.id == Payment.order_id).where(Order.driver_id == driver_id)

        stmt = stmt.group_by(Payment.method)
        rows = (await self.db.execute(stmt)).all()

        result = {
            "cash": Decimal("0.00"),
            "card_manual": Decimal("0.00"),
            "payme": Decimal("0.00"),
            "click": Decimal("0.00"),
            "count": 0,
        }
        for row in rows:
            result[row.method.value] = Decimal(row.total)
            result["count"] += int(row.cnt)
        return result
