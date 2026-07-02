"""Initial schema: users, roles, reports, files, parameters, reference ranges,
recommendations, sessions, audit logs.

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("date_of_birth", sa.DateTime, nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "reference_ranges",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("parameter_name", sa.String(255), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("sex", sa.String(10), default="any"),
        sa.Column("min_age", sa.Integer, default=0),
        sa.Column("max_age", sa.Integer, default=120),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("critical_low", sa.Float, nullable=True),
        sa.Column("critical_high", sa.Float, nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
    )
    op.create_index("ix_reference_ranges_parameter_name", "reference_ranges", ["parameter_name"])

    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), default="Untitled Report"),
        sa.Column("report_date", sa.DateTime, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("raw_extracted_text", sa.Text, nullable=True),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("health_score", sa.Float, nullable=True),
        sa.Column("risk_category", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("report_id", sa.String(36), sa.ForeignKey("reports.id"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.Integer, nullable=False),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "extracted_parameters",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("report_id", sa.String(36), sa.ForeignKey("reports.id"), nullable=False),
        sa.Column("reference_range_id", sa.Integer, sa.ForeignKey("reference_ranges.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("raw_text", sa.String(500), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("flag", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("report_id", sa.String(36), sa.ForeignKey("reports.id"), nullable=False),
        sa.Column("parameter_name", sa.String(255), nullable=True),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token", sa.String(500), nullable=False, unique=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("is_revoked", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("user_sessions")
    op.drop_table("recommendations")
    op.drop_table("extracted_parameters")
    op.drop_table("uploaded_files")
    op.drop_table("reports")
    op.drop_index("ix_reference_ranges_parameter_name", table_name="reference_ranges")
    op.drop_table("reference_ranges")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")
