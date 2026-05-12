"""Initial Models Complete

Revision ID: 7e4393700b22
Revises: 
Create Date: 2026-04-04 19:35:20.957163

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7e4393700b22'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Services
    op.create_table('services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. Users
    op.create_table('users',
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.Enum('CLIENT', 'MASTER', 'ADMIN', name='roleenum'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('telegram_id')
    )
    
    # 3. Masters
    op.create_table('masters',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('portfolio_url', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('instagram', sa.String(length=100), nullable=True),
        sa.Column('facebook', sa.String(length=100), nullable=True),
        sa.Column('tiktok', sa.String(length=100), nullable=True),
        sa.Column('telegram', sa.String(length=100), nullable=True),
        sa.Column('whatsapp', sa.String(length=100), nullable=True),
        sa.Column('viber', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # 4. Service Proposals
    op.create_table('service_proposals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_id', sa.BigInteger(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('category_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['master_id'], ['masters.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 5. Master Services
    op.create_table('master_services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_id', sa.BigInteger(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['master_id'], ['masters.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 6. Bookings
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_id', sa.BigInteger(), nullable=False),
        sa.Column('master_id', sa.BigInteger(), nullable=False),
        sa.Column('master_service_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'REJECTED', 'PROPOSED', name='bookingstatusenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_reviewed_by_client', sa.Boolean(), nullable=True),
        sa.Column('is_reviewed_by_master', sa.Boolean(), nullable=True),
        sa.Column('is_reminder_sent', sa.Boolean(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_id'], ['masters.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['master_service_id'], ['master_services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 7. Reviews
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_role', sa.Enum('CLIENT', 'MASTER', 'ADMIN', name='roleenum'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )

    # 8. Social Post Queue
    op.create_table('social_post_queue',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ad_type', sa.String(length=20), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('media_file_id', sa.String(length=255), nullable=True),
        sa.Column('media_type', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('social_post_queue')
    op.drop_table('reviews')
    op.drop_table('bookings')
    op.drop_table('master_services')
    op.drop_table('service_proposals')
    op.drop_table('masters')
    op.drop_table('users')
    op.drop_table('services')
