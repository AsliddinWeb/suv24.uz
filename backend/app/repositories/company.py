from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


class CompanyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, company_id: UUID) -> Company | None:
        stmt = select(Company).where(
            Company.id == company_id,
            Company.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Company | None:
        stmt = select(Company).where(
            Company.slug == slug,
            Company.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def create(self, company: Company) -> Company:
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)
        return company
