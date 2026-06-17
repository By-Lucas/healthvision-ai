"""add findings json column to analyses

Revision ID: 0002_add_findings
Revises: 0001_initial
Create Date: 2026-02-01 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_findings"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("analyses", sa.Column("findings", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("analyses", "findings")
