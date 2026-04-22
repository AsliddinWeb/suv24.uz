"""orders + order_items + order_status_logs + status/source enums

Revision ID: 0006_orders
Revises: 0005_drivers
Create Date: 2026-04-20 21:30:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_orders"
down_revision: Union[str, None] = "0005_drivers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


order_status_enum = postgresql.ENUM(
    "pending", "assigned", "in_delivery", "delivered", "failed", "cancelled",
    name="order_status",
    create_type=False,
)

order_source_enum = postgresql.ENUM(
    "operator", "qr", "subscription", "admin",
    name="order_source",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE order_status AS ENUM "
        "('pending','assigned','in_delivery','delivered','failed','cancelled')"
    )
    op.execute(
        "CREATE TYPE order_source AS ENUM "
        "('operator','qr','subscription','admin')"
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "number",
            sa.BigInteger(),
            sa.Identity(start=1001, increment=1),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "address_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_addresses.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "driver_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", order_status_enum, nullable=False, server_default="pending"),
        sa.Column("source", order_source_enum, nullable=False, server_default="operator"),
        sa.Column("total", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("delivery_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("number", name="uq_orders_number"),
    )
    op.create_index(
        "ix_orders_company_status_created_at",
        "orders",
        ["company_id", "status", sa.text("created_at DESC")],
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_driver_status", "orders", ["driver_id", "status"])
    op.create_index("ix_orders_deleted_at", "orders", ["deleted_at"])

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("total", sa.Numeric(14, 2), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("unit_price > 0", name="ck_order_items_unit_price_positive"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table(
        "order_status_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", order_status_enum, nullable=True),
        sa.Column("to_status", order_status_enum, nullable=False),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_order_status_logs_order_id", "order_status_logs", ["order_id"])


def downgrade() -> None:
    op.drop_index("ix_order_status_logs_order_id", table_name="order_status_logs")
    op.drop_table("order_status_logs")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_deleted_at", table_name="orders")
    op.drop_index("ix_orders_driver_status", table_name="orders")
    op.drop_index("ix_orders_customer_id", table_name="orders")
    op.drop_index("ix_orders_company_status_created_at", table_name="orders")
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS order_source")
    op.execute("DROP TYPE IF EXISTS order_status")
