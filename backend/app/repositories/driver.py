from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver import Driver


class DriverRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base(self, company_id: UUID):
        return select(Driver).where(
            Driver.company_id == company_id,
            Driver.deleted_at.is_(None),
        )

    async def get(self, company_id: UUID, driver_id: UUID) -> Driver | None:
        stmt = self._base(company_id).where(Driver.id == driver_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_user_id(self, company_id: UUID, user_id: UUID) -> Driver | None:
        stmt = self._base(company_id).where(Driver.user_id == user_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_all(self, company_id: UUID, *, only_active: bool = False) -> list[Driver]:
        stmt = self._base(company_id).order_by(Driver.created_at.desc())
        if only_active:
            stmt = stmt.where(Driver.is_active.is_(True))
        return list((await self.db.execute(stmt)).scalars().all())

    async def create(self, driver: Driver) -> Driver:
        self.db.add(driver)
        await self.db.flush()
        await self.db.refresh(driver)
        return driver

    async def delete(self, driver: Driver) -> None:
        driver.deleted_at = func.now()  # type: ignore[assignment]
        await self.db.flush()
