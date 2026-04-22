"""customers + customer_addresses + trigram indexes

Revision ID: 0003_customers
Revises: 0002_users
Create Date: 2026-04-20 20:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_customers"
down_revision: Union[str, None] = "0002_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


customer_segment_enum = postgresql.ENUM(
    "new", "active", "vip", "sleeping",
    name="customer_segment",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "CREATE TYPE customer_segment AS ENUM ('new','active','vip','sleeping')"
    )

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("segment", customer_segment_enum, nullable=False, server_default="new"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("balance", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("bottle_debt", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("company_id", "phone", name="uq_customers_company_phone"),
    )
    op.create_index("ix_customers_company_id", "customers", ["company_id"])
    op.create_index("ix_customers_phone", "customers", ["phone"])
    op.create_index("ix_customers_deleted_at", "customers", ["deleted_at"])
    op.execute(
        "CREATE INDEX ix_customers_full_name_trgm ON customers "
        "USING GIN (full_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX ix_customers_phone_trgm ON customers "
        "USING GIN (phone gin_trgm_ops)"
    )

    op.create_table(
        "customer_addresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("label", sa.String(64), nullable=False, server_default="Uy"),
        sa.Column("address_text", sa.Text(), nullable=False),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("qr_token", sa.String(32), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_customer_addresses_customer_id", "customer_addresses", ["customer_id"])
    op.create_index("ix_customer_addresses_qr_token", "customer_addresses", ["qr_token"], unique=True)
    op.create_index("ix_customer_addresses_deleted_at", "customer_addresses", ["deleted_at"])
    op.execute(
        "CREATE INDEX ix_customer_addresses_address_text_trgm ON customer_addresses "
        "USING GIN (address_text gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_customer_addresses_address_text_trgm")
    op.drop_index("ix_customer_addresses_deleted_at", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_qr_token", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_customer_id", table_name="customer_addresses")
    op.drop_table("customer_addresses")

    op.execute("DROP INDEX IF EXISTS ix_customers_phone_trgm")
    op.execute("DROP INDEX IF EXISTS ix_customers_full_name_trgm")
    op.drop_index("ix_customers_deleted_at", table_name="customers")
    op.drop_index("ix_customers_phone", table_name="customers")
    op.drop_index("ix_customers_company_id", table_name="customers")
    op.drop_table("customers")
    op.execute("DROP TYPE IF EXISTS customer_segment")
