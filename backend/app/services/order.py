from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import CustomerAddress
from app.models.driver import Driver
from app.models.order import (
    ALLOWED_TRANSITIONS,
    REASON_REQUIRED,
    Order,
    OrderItem,
    OrderSource,
    OrderStatus,
    OrderStatusLog,
)
from app.models.product import Product
from app.repositories.address import AddressRepository
from app.repositories.customer import CustomerRepository
from app.repositories.driver import DriverRepository
from app.repositories.order import OrderRepository
from app.repositories.product import PriceRepository, ProductRepository
from app.schemas.order import OrderCreate
from app.services.bottle import BottleService



class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.orders = OrderRepository(db)
        self.customers = CustomerRepository(db)
        self.addresses = AddressRepository(db)
        self.products = ProductRepository(db)
        self.prices = PriceRepository(db)
        self.drivers = DriverRepository(db)

    async def _validate_address(
        self, customer_id: UUID, address_id: UUID
    ) -> CustomerAddress:
        address = await self.addresses.get(customer_id, address_id)
        if address is None or not address.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Address not found or inactive for this customer",
            )
        return address

    async def _load_product(self, company_id: UUID, product_id: UUID) -> Product:
        product = await self.products.get(company_id, product_id)
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product_id} not found or inactive",
            )
        return product

    async def create_order(
        self,
        company_id: UUID,
        actor_user_id: UUID,
        data: OrderCreate,
    ) -> Order:
        customer = await self.customers.get(company_id, data.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        await self._validate_address(customer.id, data.address_id)

        order_items: list[OrderItem] = []
        total = Decimal("0.00")
        for item in data.items:
            product = await self._load_product(company_id, item.product_id)
            current_price_row = await self.prices.get_current(product.id)
            if current_price_row is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {product.name} has no active price",
                )
            line_total = current_price_row.price * item.quantity
            total += line_total
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=current_price_row.price,
                    total=line_total,
                    product_name=product.name,
                )
            )

        order = Order(
            company_id=company_id,
            customer_id=customer.id,
            address_id=data.address_id,
            status=OrderStatus.PENDING,
            source=data.source,
            total=total,
            delivery_window_start=data.delivery_window_start,
            delivery_window_end=data.delivery_window_end,
            notes=data.notes,
            created_by_user_id=actor_user_id,
            items=order_items,
        )
        self.db.add(order)
        await self.db.flush()

        self.db.add(
            OrderStatusLog(
                order_id=order.id,
                from_status=None,
                to_status=OrderStatus.PENDING,
                actor_user_id=actor_user_id,
                reason=None,
            )
        )
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def _transition(
        self,
        order: Order,
        to_status: OrderStatus,
        *,
        actor_user_id: UUID,
        reason: str | None = None,
    ) -> Order:
        if order.is_terminal:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Order is in terminal status: {order.status.value}",
            )
        allowed = ALLOWED_TRANSITIONS.get(order.status, set())
        if to_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid transition: {order.status.value} → {to_status.value}",
            )
        if to_status in REASON_REQUIRED and not reason:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Reason is required to transition to {to_status.value}",
            )

        from_status = order.status
        order.status = to_status
        if to_status == OrderStatus.CANCELLED:
            order.cancel_reason = reason

        self.db.add(
            OrderStatusLog(
                order_id=order.id,
                from_status=from_status,
                to_status=to_status,
                actor_user_id=actor_user_id,
                reason=reason,
            )
        )

        if to_status == OrderStatus.DELIVERED:
            customer = await self.customers.get(order.company_id, order.customer_id)
            if customer is not None:
                customer.balance = (customer.balance or Decimal("0")) + order.total

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def assign_driver(
        self,
        order: Order,
        driver: Driver,
        actor_user_id: UUID,
    ) -> Order:
        if not driver.is_active:
            raise HTTPException(status_code=400, detail="Driver is not active")
        if order.company_id != driver.company_id:
            raise HTTPException(status_code=400, detail="Driver belongs to another company")
        if order.status not in {OrderStatus.PENDING, OrderStatus.ASSIGNED}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot assign from status {order.status.value}",
            )
        previous_driver = order.driver_id
        order.driver_id = driver.id
        if order.status == OrderStatus.PENDING:
            await self._transition(
                order,
                OrderStatus.ASSIGNED,
                actor_user_id=actor_user_id,
                reason=None,
            )
        elif previous_driver != driver.id:
            self.db.add(
                OrderStatusLog(
                    order_id=order.id,
                    from_status=OrderStatus.ASSIGNED,
                    to_status=OrderStatus.ASSIGNED,
                    actor_user_id=actor_user_id,
                    reason=f"Reassigned driver to {driver.id}",
                )
            )
            await self.db.flush()
        return order

    async def unassign_driver(self, order: Order, actor_user_id: UUID) -> Order:
        if order.status != OrderStatus.ASSIGNED:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot unassign from status {order.status.value}",
            )
        order.driver_id = None
        return await self._transition(
            order,
            OrderStatus.PENDING,
            actor_user_id=actor_user_id,
            reason="Unassigned",
        )

    async def start_delivery(self, order: Order, actor_user_id: UUID) -> Order:
        return await self._transition(
            order, OrderStatus.IN_DELIVERY, actor_user_id=actor_user_id
        )

    async def mark_delivered(
        self,
        order: Order,
        actor_user_id: UUID,
        bottle_returns: dict[UUID, int] | None = None,
    ) -> Order:
        customer = await self.customers.get(order.company_id, order.customer_id)
        driver = (
            await self.drivers.get(order.company_id, order.driver_id)
            if order.driver_id
            else None
        )

        order = await self._transition(
            order, OrderStatus.DELIVERED, actor_user_id=actor_user_id
        )

        if customer is not None:
            bottle_service = BottleService(self.db)
            await bottle_service.apply_delivery(
                order=order,
                customer=customer,
                driver=driver,
                bottle_returns=bottle_returns or {},
            )
            await self.db.refresh(customer)

        return order

    async def mark_failed(
        self, order: Order, actor_user_id: UUID, reason: str
    ) -> Order:
        return await self._transition(
            order, OrderStatus.FAILED, actor_user_id=actor_user_id, reason=reason
        )

    async def cancel(self, order: Order, actor_user_id: UUID, reason: str) -> Order:
        return await self._transition(
            order, OrderStatus.CANCELLED, actor_user_id=actor_user_id, reason=reason
        )

    async def retry(self, order: Order, actor_user_id: UUID) -> Order:
        order.driver_id = None
        return await self._transition(
            order, OrderStatus.PENDING, actor_user_id=actor_user_id, reason="Retry"
        )
