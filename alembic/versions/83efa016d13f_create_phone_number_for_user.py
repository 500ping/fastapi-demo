"""Create phone number for user

Revision ID: 83efa016d13f
Revises: 
Create Date: 2023-10-17 15:52:51.896769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83efa016d13f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column(
        "phone_number", sa.String(), nullable=True))


def downgrade() -> None:
    pass
