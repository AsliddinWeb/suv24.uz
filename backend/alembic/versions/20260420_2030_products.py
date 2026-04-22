"""products + product_prices with partial unique on current price

Revision ID: 0004_products
Revises: 0003_customers
Create Date: 2026-04-20 20:30:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_products"
down_revision: Union[str, None] = "0003_customers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("volume_liters", sa.Integer(), nullable=False),
        sa.Column("is_returnable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_products_company_id", "products", ["company_id"])
    op.create_index("ix_products_deleted_at", "products", ["deleted_at"])

    op.create_table(
        "product_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("price > 0", name="ck_product_prices_price_positive"),
    )
    op.create_index("ix_product_prices_product_id", "product_prices", ["product_id"])
    op.execute(
        "CREATE UNIQUE INDEX uq_product_prices_current "
        "ON product_prices (product_id) WHERE valid_to IS NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_product_prices_current")
    op.drop_index("ix_product_prices_product_id", table_name="product_prices")
    op.drop_table("product_prices")
    op.drop_index("ix_products_deleted_at", table_name="products")
    op.drop_index("ix_products_company_id", table_name="products")
    op.drop_table("products")
