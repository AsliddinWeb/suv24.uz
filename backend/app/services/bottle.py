from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bottle import DriverBottleBalance
from app.models.customer import Customer
from app.models.driver import Driver
from app.models.order import Order, OrderItem
from app.repositories.bottle import BottleBalanceRepository
from app.repositories.product import ProductRepository


class BottleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.balances = BottleBalanceRepository(db)
        self.products = ProductRepository(db)

    async def adjust_driver_balance(
        self,
        driver: Driver,
        product_id: UUID,
        full_delta: int,
        empty_delta: int,
    ) -> DriverBottleBalance:
        product = await self.products.get(driver.company_id, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if not product.is_returnable:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Product is not returnable",
            )
        balance = await self.balances.get_or_create(driver.id, product_id)
        balance.full_count += full_delta
        balance.empty_count += empty_delta
        if balance.full_count < 0 or balance.empty_count < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Adjustment would make balance negative",
            )
        await self.db.flush()
        await self.db.refresh(balance)
        return balance

    async def apply_delivery(
        self,
        order: Order,
        customer: Customer,
        driver: Driver | None,
        bottle_returns: dict[UUID, int],
    ) -> None:
        """
        On delivery:
        - For each returnable product in order: customer.bottle_debt += qty, driver.full -= qty.
        - For each returned empty: customer.bottle_debt -= count, driver.empty += count.
        Driver may be None if order was delivered without assignment (edge case).
        """
        returnable_products: dict[UUID, int] = {}
        for item in order.items:
            product = await self.products.get(order.company_id, item.product_id)
            if product is None or not product.is_returnable:
                continue
            returnable_products[item.product_id] = (
                returnable_products.get(item.product_id, 0) + item.quantity
            )

        for product_id, qty in returnable_products.items():
            customer.bottle_debt += qty
            if driver is not None:
                balance = await self.balances.get_or_create(driver.id, product_id)
                if balance.full_count < qty:
                    product = await self.products.get(order.company_id, product_id)
                    name = product.name if product else str(product_id)
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            f"Haydovchida yetarli to'la idish yo'q: "
                            f"{name} · bor: {balance.full_count}, kerak: {qty}. "
                            f"Admin paneldan haydovchiga idish yuklang."
                        ),
                    )
                balance.full_count -= qty

        for product_id, returned in bottle_returns.items():
            product = await self.products.get(order.company_id, product_id)
            if product is None or not product.is_returnable:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Product {product_id} is not returnable",
                )
            customer.bottle_debt = max(0, customer.bottle_debt - returned)
            if driver is not None:
                balance = await self.balances.get_or_create(driver.id, product_id)
                balance.empty_count += returned

        await self.db.flush()
