from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductPrice
from app.repositories.product import PriceRepository, ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.products = ProductRepository(db)
        self.prices = PriceRepository(db)

    async def create_product(self, company_id: UUID, data: ProductCreate) -> Product:
        product = Product(
            company_id=company_id,
            name=data.name,
            volume_liters=data.volume_liters,
            is_returnable=data.is_returnable,
            is_active=data.is_active,
        )
        product = await self.products.create(product)

        price = ProductPrice(
            product_id=product.id,
            price=data.initial_price,
            valid_from=datetime.now(tz=timezone.utc),
            valid_to=None,
        )
        await self.prices.create(price)
        return product

    async def update_product(self, product: Product, data: ProductUpdate) -> Product:
        changed = data.model_dump(exclude_unset=True)
        for field, value in changed.items():
            setattr(product, field, value)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def set_price(self, product: Product, new_price: Decimal) -> ProductPrice:
        if new_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price must be positive",
            )

        now = datetime.now(tz=timezone.utc)
        current = await self.prices.get_current(product.id)
        if current is not None:
            if current.price == new_price:
                return current
            current.valid_to = now
            await self.db.flush()

        new_row = ProductPrice(
            product_id=product.id,
            price=new_price,
            valid_from=now,
            valid_to=None,
        )
        return await self.prices.create(new_row)

    async def current_price(self, product: Product) -> Decimal | None:
        row = await self.prices.get_current(product.id)
        return row.price if row else None
