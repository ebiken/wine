"""vineyard_grape_variety junction

Revision ID: b3e4f5a6b7c8
Revises: 9f2a8c1d4b00
Create Date: 2026-04-06

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "9f2a8c1d4b00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vineyard_grape_variety",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vineyard_id", sa.Integer(), nullable=False),
        sa.Column("grape_variety_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["grape_variety_id"], ["grape_variety.id"]),
        sa.ForeignKeyConstraint(["vineyard_id"], ["vineyard.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vineyard_id", "grape_variety_id"),
    )


def downgrade() -> None:
    op.drop_table("vineyard_grape_variety")
