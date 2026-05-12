"""add reminder flag

Revision ID: 4934208d0bf9
Revises: 2aa58bd08017
Create Date: 2026-04-18 10:48:47.382025

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4934208d0bf9'
down_revision: Union[str, None] = '2aa58bd08017'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
