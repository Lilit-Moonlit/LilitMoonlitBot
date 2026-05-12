"""Add reviews and booking flags

Revision ID: 2aa58bd08017
Revises: 7e4393700b22
Create Date: 2026-04-07 15:29:42.136687

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2aa58bd08017'
down_revision: Union[str, None] = '7e4393700b22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
