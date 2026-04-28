"""cash account, cash transactions, inventory purchases

Revision ID: 0013_cash
Revises: 0012_warehouse
Create Date: 2026-04-28 12:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_cash"
down_revision: Union[str, None] = "0012_warehouse"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Inventory purchases — must come before cash_transactions because of FK
    op.create_table(
        "inventory_purchases",
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
        sa.Column("unit_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("supplier", sa.String(255), nullable=True),
        sa.Column("note", sa.String(512), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column(
            "actor_user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
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

    # Cash account — one row per company
    op.create_table(
        "cash_accounts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            unique=True,
        ),
        sa.Column("balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(8), nullable=False, server_default="UZS"),
        sa.Column("opening_set_at", sa.DateTime(timezone=True), nullable=True),
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

    # Cash transactions — append-only ledger; let create_table handle the enum.
    op.create_table(
        "cash_transactions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "kind",
            sa.Enum(
                "opening_balance",
                "purchase",
                "expense",
                "customer_payment",
                "refund",
                "manual_in",
                "manual_out",
                name="cash_transaction_kind",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column(
            "actor_user_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "related_purchase_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_purchases.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "related_payment_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payments.id", ondelete="SET NULL"),
            nullable=True,
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
    op.drop_table("cash_transactions")
    op.drop_table("cash_accounts")
    op.drop_table("inventory_purchases")
    op.execute("DROP TYPE IF EXISTS cash_transaction_kind")
