"""driver_bottle_balance table

Revision ID: 0008_driver_bottle_balance
Revises: 0007_payments
Create Date: 2026-04-21 09:30:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_driver_bottle_balance"
down_revision: Union[str, None] = "0007_payments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "driver_bottle_balance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "driver_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("full_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("empty_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("driver_id", "product_id", name="uq_driver_bottle_driver_product"),
        sa.CheckConstraint("full_count >= 0", name="ck_driver_bottle_full_nonneg"),
        sa.CheckConstraint("empty_count >= 0", name="ck_driver_bottle_empty_nonneg"),
    )
    op.create_index("ix_driver_bottle_balance_driver_id", "driver_bottle_balance", ["driver_id"])
    op.create_index("ix_driver_bottle_balance_product_id", "driver_bottle_balance", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_driver_bottle_balance_product_id", table_name="driver_bottle_balance")
    op.drop_index("ix_driver_bottle_balance_driver_id", table_name="driver_bottle_balance")
    op.drop_table("driver_bottle_balance")
