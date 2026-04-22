import enum

from sqlalchemy import Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    REJECTED = "rejected"


class Lead(Base, TimestampMixin, SoftDeleteMixin):
    """Demo / trial request captured from the public landing page."""

    __tablename__ = "leads"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="landing")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(
            LeadStatus,
            name="lead_status",
            native_enum=True,
            values_callable=lambda e: [v.value for v in e],
        ),
        nullable=False,
        default=LeadStatus.NEW,
    )

    def __repr__(self) -> str:
        return f"<Lead {self.full_name} {self.phone} status={self.status.value}>"
