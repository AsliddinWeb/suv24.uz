from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.payments = PaymentRepository(db)
        self.orders = OrderRepository(db)
        self.customers = CustomerRepository(db)

    async def record_payment(
        self,
        company_id: UUID,
        actor_user_id: UUID,
        data: PaymentCreate,
    ) -> Payment:
        order = await self.orders.get(company_id, data.order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot record payment for cancelled order",
            )

        already_paid = await self.payments.total_paid_for_order(order.id)
        outstanding = order.total - already_paid
        if outstanding <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Order is already fully paid",
            )
        if data.amount > outstanding:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Amount exceeds outstanding balance ({outstanding})",
            )

        new_paid_total = already_paid + data.amount
        resulting_status = (
            PaymentStatus.PAID if new_paid_total >= order.total else PaymentStatus.PARTIAL
        )

        payment = Payment(
            company_id=company_id,
            order_id=order.id,
            customer_id=order.customer_id,
            amount=data.amount,
            method=data.method,
            status=resulting_status,
            provider_tx_id=data.provider_tx_id,
            recorded_by_user_id=actor_user_id,
            notes=data.notes,
        )
        payment = await self.payments.create(payment)

        customer = await self.customers.get(company_id, order.customer_id)
        if customer is not None:
            customer.balance = (customer.balance or Decimal("0")) - data.amount
            await self.db.flush()

        return payment

    async def refund(
        self,
        company_id: UUID,
        payment: Payment,
        actor_user_id: UUID,
        reason: str | None,
    ) -> Payment:
        if payment.status == PaymentStatus.REFUNDED:
            raise HTTPException(status_code=409, detail="Payment already refunded")
        if payment.status != PaymentStatus.PAID and payment.status != PaymentStatus.PARTIAL:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot refund a {payment.status.value} payment",
            )

        payment.status = PaymentStatus.REFUNDED
        payment.notes = (payment.notes or "") + (f"\n[refund] {reason}" if reason else "\n[refund]")

        customer = await self.customers.get(company_id, payment.customer_id)
        if customer is not None:
            customer.balance = (customer.balance or Decimal("0")) + payment.amount
            await self.db.flush()

        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def order_outstanding(self, order: Order) -> Decimal:
        paid = await self.payments.total_paid_for_order(order.id)
        return order.total - paid
