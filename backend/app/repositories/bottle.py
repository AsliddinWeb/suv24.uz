from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bottle import DriverBottleBalance


class BottleBalanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, driver_id: UUID, product_id: UUID) -> DriverBottleBalance | None:
        stmt = select(DriverBottleBalance).where(
            DriverBottleBalance.driver_id == driver_id,
            DriverBottleBalance.product_id == product_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_or_create(self, driver_id: UUID, product_id: UUID) -> DriverBottleBalance:
        existing = await self.get(driver_id, product_id)
        if existing is not None:
            return existing
        row = DriverBottleBalance(
            driver_id=driver_id,
            product_id=product_id,
            full_count=0,
            empty_count=0,
        )
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def list_for_driver(self, driver_id: UUID) -> list[DriverBottleBalance]:
        stmt = select(DriverBottleBalance).where(DriverBottleBalance.driver_id == driver_id)
        return list((await self.db.execute(stmt)).scalars().all())
