"""worklog payment domain

Revision ID: b7c2e1f4a8d0
Revises: 1a31ce608336
Create Date: 2025-03-25

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b7c2e1f4a8d0"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "task",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("hourly_rate", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_title"), "task", ["title"], unique=False)

    op.create_table(
        "worklog",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("freelancer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["freelancer_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_worklog_created_at"), "worklog", ["created_at"], unique=False
    )
    op.create_index(
        op.f("ix_worklog_freelancer_id"), "worklog", ["freelancer_id"], unique=False
    )
    op.create_index(op.f("ix_worklog_status"), "worklog", ["status"], unique=False)
    op.create_index(op.f("ix_worklog_task_id"), "worklog", ["task_id"], unique=False)

    op.create_table(
        "time_entry",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worklog_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.ForeignKeyConstraint(["worklog_id"], ["worklog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_time_entry_worked_at"), "time_entry", ["worked_at"], unique=False
    )
    op.create_index(
        op.f("ix_time_entry_worklog_id"), "time_entry", ["worklog_id"], unique=False
    )

    op.create_table(
        "payment_batch",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("worklog_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_payment_batch_created_at"),
        "payment_batch",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "payment_batch_worklog",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worklog_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["payment_batch.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["worklog_id"], ["worklog.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_payment_batch_worklog_batch_id"),
        "payment_batch_worklog",
        ["batch_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_payment_batch_worklog_batch_id"), table_name="payment_batch_worklog"
    )
    op.drop_table("payment_batch_worklog")
    op.drop_index(op.f("ix_payment_batch_created_at"), table_name="payment_batch")
    op.drop_table("payment_batch")
    op.drop_index(op.f("ix_time_entry_worklog_id"), table_name="time_entry")
    op.drop_index(op.f("ix_time_entry_worked_at"), table_name="time_entry")
    op.drop_table("time_entry")
    op.drop_index(op.f("ix_worklog_task_id"), table_name="worklog")
    op.drop_index(op.f("ix_worklog_status"), table_name="worklog")
    op.drop_index(op.f("ix_worklog_freelancer_id"), table_name="worklog")
    op.drop_index(op.f("ix_worklog_created_at"), table_name="worklog")
    op.drop_table("worklog")
    op.drop_index(op.f("ix_task_title"), table_name="task")
    op.drop_table("task")
