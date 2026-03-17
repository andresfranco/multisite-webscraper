"""Initial schema with scrape_configs, scrape_jobs, scraped_items, job_logs.

Revision ID: 001_initial
Revises:
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # scrape_configs
    op.create_table(
        "scrape_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("base_url", sa.String(2048), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("use_headless_browser", sa.Boolean(), server_default="false"),
        sa.Column("wait_for_selector", sa.String(500), nullable=True),
        sa.Column("custom_headers", postgresql.JSONB(), nullable=True),
        sa.Column("pagination_type", sa.String(20), server_default="none"),
        sa.Column("pagination_selector", sa.String(500), nullable=True),
        sa.Column("max_pages", sa.Integer(), server_default="1"),
        sa.Column("item_selector", sa.String(500), nullable=False),
        sa.Column("fields", postgresql.JSONB(), nullable=False),
        sa.Column("request_delay_ms", sa.Integer(), server_default="1000"),
        sa.Column("concurrent_requests", sa.Integer(), server_default="1"),
        sa.Column("schedule_cron", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_scrape_configs_domain", "scrape_configs", ["domain"])

    # scrape_jobs
    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("config_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pages_scraped", sa.Integer(), server_default="0"),
        sa.Column("items_found", sa.Integer(), server_default="0"),
        sa.Column("items_created", sa.Integer(), server_default="0"),
        sa.Column("items_skipped", sa.Integer(), server_default="0"),
        sa.Column("errors", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["config_id"],
            ["scrape_configs.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index("idx_scrape_jobs_status", "scrape_jobs", ["status"])

    # scraped_items
    op.create_table(
        "scraped_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("config_id", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("item_url", sa.String(2048), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_hash"),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["scrape_jobs.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["config_id"],
            ["scrape_configs.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index("idx_scraped_items_config", "scraped_items", ["config_id"])
    op.create_index("idx_scraped_items_job", "scraped_items", ["job_id"])
    op.create_index(
        "idx_scraped_items_data",
        "scraped_items",
        ["data"],
        postgresql_using="gin",
    )

    # job_logs
    op.create_table(
        "job_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(10), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["scrape_jobs.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("idx_job_logs_job", "job_logs", ["job_id"])


def downgrade() -> None:
    op.drop_table("job_logs")
    op.drop_table("scraped_items")
    op.drop_table("scrape_jobs")
    op.drop_table("scrape_configs")
