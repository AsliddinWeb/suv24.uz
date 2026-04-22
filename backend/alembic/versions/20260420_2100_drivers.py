"""drivers table (1:1 with users)

Revision ID: 0005_drivers
Revises: 0004_products
Create Date: 2026-04-20 21:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_drivers"
down_revision: Union[str, None] = "0004_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("vehicle_plate", sa.String(32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("current_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("current_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_drivers_company_id", "drivers", ["company_id"])
    op.create_index("ix_drivers_user_id", "drivers", ["user_id"], unique=True)
    op.create_index("ix_drivers_deleted_at", "drivers", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_drivers_deleted_at", table_name="drivers")
    op.drop_index("ix_drivers_user_id", table_name="drivers")
    op.drop_index("ix_drivers_company_id", table_name="drivers")
    op.drop_table("drivers")
