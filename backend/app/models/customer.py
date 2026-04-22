import enum
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CompanyScopedMixin, SoftDeleteMixin, TimestampMixin


class CustomerSegment(str, enum.Enum):
    NEW = "new"
    ACTIVE = "active"
    VIP = "vip"
    SLEEPING = "sleeping"


class Customer(Base, TimestampMixin, SoftDeleteMixin, CompanyScopedMixin):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("company_id", "phone", name="uq_customers_company_phone"),
    )

    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    segment: Mapped[CustomerSegment] = mapped_column(
        SAEnum(
            CustomerSegment,
            name="customer_segment",
            native_enum=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
        default=CustomerSegment.NEW,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    bottle_debt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    addresses: Mapped[list["CustomerAddress"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Customer {self.phone} {self.full_name}>"


class CustomerAddress(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customer_addresses"

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(64), nullable=False, default="Uy")
    address_text: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    qr_token: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"<CustomerAddress {self.label} qr={self.qr_token}>"
