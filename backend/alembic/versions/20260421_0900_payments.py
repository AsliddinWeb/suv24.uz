"""payments table + payment_method / payment_status enums

Revision ID: 0007_payments
Revises: 0006_orders
Create Date: 2026-04-21 09:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_payments"
down_revision: Union[str, None] = "0006_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


payment_method_enum = postgresql.ENUM(
    "cash", "card_manual", "payme", "click",
    name="payment_method",
    create_type=False,
)

payment_status_enum = postgresql.ENUM(
    "pending", "processing", "paid", "partial", "failed", "refunded", "cancelled",
    name="payment_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE payment_method AS ENUM ('cash','card_manual','payme','click')"
    )
    op.execute(
        "CREATE TYPE payment_status AS ENUM "
        "('pending','processing','paid','partial','failed','refunded','cancelled')"
    )

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("method", payment_method_enum, nullable=False),
        sa.Column("status", payment_status_enum, nullable=False),
        sa.Column("provider_tx_id", sa.String(128), nullable=True, unique=True),
        sa.Column(
            "recorded_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )
    op.create_index("ix_payments_company_id", "payments", ["company_id"])
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_customer_id", "payments", ["customer_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_created_at", "payments", [sa.text("created_at DESC")])
    op.create_index("ix_payments_deleted_at", "payments", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_payments_deleted_at", table_name="payments")
    op.drop_index("ix_payments_created_at", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_customer_id", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_index("ix_payments_company_id", table_name="payments")
    op.drop_table("payments")
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS payment_method")
