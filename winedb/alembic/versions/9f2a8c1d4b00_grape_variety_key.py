"""add grape_variety.key

Revision ID: 9f2a8c1d4b00
Revises: 817101459347
Create Date: 2026-04-06

"""
from __future__ import annotations

import re
import unicodedata
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9f2a8c1d4b00"
down_revision: Union[str, Sequence[str], None] = "817101459347"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slug(display_name: str) -> str:
    s = unicodedata.normalize("NFKD", display_name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def upgrade() -> None:
    op.add_column("grape_variety", sa.Column("key", sa.Text(), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, name FROM grape_variety")).fetchall()
    for row in rows:
        rid, name = int(row[0]), str(row[1])
        bind.execute(
            sa.text("UPDATE grape_variety SET key = :k WHERE id = :id"),
            {"k": _slug(name), "id": rid},
        )
    op.create_index(
        "uq_grape_variety_key",
        "grape_variety",
        ["key"],
        unique=True,
    )
    with op.batch_alter_table("grape_variety") as batch_op:
        batch_op.alter_column("key", existing_type=sa.Text(), nullable=False)


def downgrade() -> None:
    op.drop_index("uq_grape_variety_key", table_name="grape_variety")
    op.drop_column("grape_variety", "key")
