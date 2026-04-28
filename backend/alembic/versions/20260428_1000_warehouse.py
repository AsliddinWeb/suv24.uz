"""warehouse stock + stock movements

Revision ID: 0012_warehouse
Revises: 0011_leads
Create Date: 2026-04-28 10:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_warehouse"
down_revision: Union[str, None] = "0011_leads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Warehouse stock per (company, product)
    op.create_table(
        "warehouse_stock",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("full_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("empty_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("company_id", "product_id", name="uq_warehouse_company_product"),
        sa.CheckConstraint("full_count >= 0", name="ck_warehouse_full_nonneg"),
        sa.CheckConstraint("empty_count >= 0", name="ck_warehouse_empty_nonneg"),
    )

    # Audit trail of warehouse changes
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("full_delta", sa.Integer, nullable=False, server_default="0"),
        sa.Column("empty_delta", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "driver_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column(
            "actor_user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("warehouse_stock")
