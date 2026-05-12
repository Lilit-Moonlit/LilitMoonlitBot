"""Add SocialPostQueue table

Revision ID: ddc0abf7a52f
Revises: d708d9ad9836
Create Date: 2026-05-05 17:13:43.379655

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ddc0abf7a52f'
down_revision: Union[str, None] = 'd708d9ad9836'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
