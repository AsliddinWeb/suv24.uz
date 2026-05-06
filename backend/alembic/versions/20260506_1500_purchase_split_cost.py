"""split inventory_purchases.unit_cost into unit_cost_full + unit_cost_empty

Revision ID: 0014_purchase_split_cost
Revises: 0013_cash
Create Date: 2026-05-06 15:00:00

Empty bottles (returned containers) shouldn't share the same per-unit cost as
full bottles. We rename the existing `unit_cost` column to `unit_cost_full` and
add a new `unit_cost_empty` (default 0) so each side can be priced independently.
Existing rows keep their `total_cost` untouched — only future receipts use the
split formula.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_purchase_split_cost"
down_revision: Union[str, None] = "0013_cash"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "inventory_purchases",
        "unit_cost",
        new_column_name="unit_cost_full",
    )
    op.add_column(
        "inventory_purchases",
        sa.Column(
            "unit_cost_empty",
            sa.Numeric(14, 2),
            nullable=False,
            server_default="0",
        ),
    )
    # Drop server default — application is responsible going forward.
    op.alter_column(
        "inventory_purchases",
        "unit_cost_empty",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("inventory_purchases", "unit_cost_empty")
    op.alter_column(
        "inventory_purchases",
        "unit_cost_full",
        new_column_name="unit_cost",
    )
