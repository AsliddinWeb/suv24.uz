"""company branding: add logo_url, short_name, support_phone

Revision ID: 0009_company_branding
Revises: 0008_driver_bottle_balance
Create Date: 2026-04-22 03:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_company_branding"
down_revision: Union[str, None] = "0008_driver_bottle_balance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("short_name", sa.String(length=32), nullable=True))
    op.add_column("companies", sa.Column("support_phone", sa.String(length=32), nullable=True))
    op.add_column("companies", sa.Column("logo_url", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("companies", "logo_url")
    op.drop_column("companies", "support_phone")
    op.drop_column("companies", "short_name")
