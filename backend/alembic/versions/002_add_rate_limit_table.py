"""Add domain_rate_limits table.

Revision ID: 002_add_rate_limit_table
Revises: 001_initial
Create Date: 2026-03-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_rate_limit_table"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_rate_limits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("domain", sa.String(255), nullable=False, unique=True),
        sa.Column("delay_ms", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("last_request", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_domain_rate_limits_domain",
        "domain_rate_limits",
        ["domain"],
    )


def downgrade() -> None:
    op.drop_index("idx_domain_rate_limits_domain", table_name="domain_rate_limits")
    op.drop_table("domain_rate_limits")
