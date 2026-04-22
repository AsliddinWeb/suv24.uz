from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductPrice


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _base(self, company_id: UUID):
        return select(Product).where(
            Product.company_id == company_id,
            Product.deleted_at.is_(None),
        )

    async def get(self, company_id: UUID, product_id: UUID) -> Product | None:
        stmt = self._base(company_id).where(Product.id == product_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_all(self, company_id: UUID, *, only_active: bool = False) -> list[Product]:
        stmt = self._base(company_id)
        if only_active:
            stmt = stmt.where(Product.is_active.is_(True))
        stmt = stmt.order_by(Product.volume_liters.desc(), Product.name.asc())
        return list((await self.db.execute(stmt)).scalars().all())

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        product.deleted_at = func.now()  # type: ignore[assignment]
        await self.db.flush()


class PriceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_current(self, product_id: UUID) -> ProductPrice | None:
        stmt = select(ProductPrice).where(
            ProductPrice.product_id == product_id,
            ProductPrice.valid_to.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_history(self, product_id: UUID) -> list[ProductPrice]:
        stmt = (
            select(ProductPrice)
            .where(ProductPrice.product_id == product_id)
            .order_by(ProductPrice.valid_from.desc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def create(self, price: ProductPrice) -> ProductPrice:
        self.db.add(price)
        await self.db.flush()
        await self.db.refresh(price)
        return price
