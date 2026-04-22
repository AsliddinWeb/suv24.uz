import enum
from uuid import UUID

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class UserRole(str, enum.Enum):
    PLATFORM_OWNER = "platform_owner"
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    DRIVER = "driver"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("company_id", "phone", name="uq_users_company_phone"),
    )

    # Nullable: platform_owner is not scoped to a single company
    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<User {self.phone} role={self.role.value}>"
