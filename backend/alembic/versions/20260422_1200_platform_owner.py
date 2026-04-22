"""platform owner role, tariff plan on companies, nullable user.company_id

Revision ID: 0010_platform_owner
Revises: 0009_company_branding
Create Date: 2026-04-22 12:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_platform_owner"
down_revision: Union[str, None] = "0009_company_branding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add platform_owner to user_role enum
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'platform_owner'")

    # Make users.company_id nullable (platform_owner has none)
    op.alter_column("users", "company_id", existing_type=sa.dialects.postgresql.UUID(), nullable=True)

    # Create tariff_plan enum
    tariff_enum = sa.Enum("trial", "start", "biznes", "premium", name="tariff_plan")
    tariff_enum.create(op.get_bind(), checkfirst=True)

    # Add tariff columns to companies
    op.add_column(
        "companies",
        sa.Column(
            "tariff_plan",
            sa.Enum("trial", "start", "biznes", "premium", name="tariff_plan", create_type=False),
            nullable=False,
            server_default="trial",
        ),
    )
    op.add_column(
        "companies",
        sa.Column("monthly_fee", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
    )
    op.add_column(
        "companies",
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("companies", "trial_ends_at")
    op.drop_column("companies", "monthly_fee")
    op.drop_column("companies", "tariff_plan")
    op.execute("DROP TYPE IF EXISTS tariff_plan")

    # Revert users.company_id to NOT NULL — only safe if no platform_owner rows exist
    op.execute("DELETE FROM users WHERE role = 'platform_owner'")
    op.alter_column("users", "company_id", existing_type=sa.dialects.postgresql.UUID(), nullable=False)
    # Note: cannot cleanly remove 'platform_owner' from enum without recreating the type.
