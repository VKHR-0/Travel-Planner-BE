"""init schema

Revision ID: ae7352e1c370
Revises:
Create Date: 2026-02-26 11:12:37.879844

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ae7352e1c370"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("trips")
