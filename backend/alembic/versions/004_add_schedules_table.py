"""Add scrape_schedules table.

Revision ID: 004_add_schedules_table
Revises: 003_add_users_table
Create Date: 2026-03-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_add_schedules_table"
down_revision: Union[str, None] = "003_add_users_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scrape_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "config_id",
            sa.Integer(),
            sa.ForeignKey("scrape_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cron_expression", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_scrape_schedules_config_id",
        "scrape_schedules",
        ["config_id"],
    )
    op.create_index(
        "idx_scrape_schedules_is_active",
        "scrape_schedules",
        ["is_active"],
    )


def downgrade() -> None:
    op.drop_index("idx_scrape_schedules_is_active", table_name="scrape_schedules")
    op.drop_index("idx_scrape_schedules_config_id", table_name="scrape_schedules")
    op.drop_table("scrape_schedules")
