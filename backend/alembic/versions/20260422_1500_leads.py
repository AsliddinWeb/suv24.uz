"""leads: demo/trial request capture from public landing

Revision ID: 0011_leads
Revises: 0010_platform_owner
Create Date: 2026-04-22 15:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_leads"
down_revision: Union[str, None] = "0010_platform_owner"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(32), nullable=False, index=True),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("source", sa.String(64), nullable=False, server_default="landing"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("new", "contacted", "converted", "rejected", name="lead_status"),
            nullable=False,
            server_default="new",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
    )
    op.create_index("ix_leads_created_at", "leads", ["created_at"])
    op.create_index("ix_leads_status", "leads", ["status"])


def downgrade() -> None:
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_created_at", table_name="leads")
    op.drop_table("leads")
    op.execute("DROP TYPE IF EXISTS lead_status")
