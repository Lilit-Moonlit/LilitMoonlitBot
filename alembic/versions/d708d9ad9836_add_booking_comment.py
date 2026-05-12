"""add booking comment

Revision ID: d708d9ad9836
Revises: 4934208d0bf9
Create Date: 2026-04-20 12:53:14.636687

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd708d9ad9836'
down_revision: Union[str, None] = '4934208d0bf9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
