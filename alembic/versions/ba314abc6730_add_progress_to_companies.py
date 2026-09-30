"""add progress to companies

Revision ID: ba314abc6730
Revises: 54b4bdc377b6
Create Date: 2026-09-21 13:04:00.208013

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ba314abc6730"
down_revision: Union[str, Sequence[str], None] = "54b4bdc377b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    progress_enum = sa.Enum(
        "active",
        "archived",
        "rejected",
        "transferred",
        name="company_progress",
    )
    progress_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "companies",
        sa.Column("progress", progress_enum, server_default="active", nullable=False),
    )
    op.create_index(
        op.f("ix_companies_progress"),
        "companies",
        ["progress"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_companies_progress"), table_name="companies")
    op.drop_column("companies", "progress")

    progress_enum = sa.Enum(name="company_progress")
    progress_enum.drop(op.get_bind(), checkfirst=True)
