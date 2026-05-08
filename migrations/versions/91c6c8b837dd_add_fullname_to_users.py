"""add fullname to users

Revision ID: 91c6c8b837dd
Revises: e6d70719889d
Create Date: 2026-05-08 19:51:56.906269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91c6c8b837dd'
down_revision = 'e6d70719889d'
branch_labels = None
depends_on = None


def upgrade():
    # Add fullname column to users table if it doesn't exist
    op.add_column('users', sa.Column('fullname', sa.String(length=255), nullable=True), schema='public')
    # Update existing rows with a default value
    op.execute("UPDATE public.users SET fullname = 'Unknown' WHERE fullname IS NULL")
    # Make it NOT NULL after setting defaults
    op.alter_column('users', 'fullname', nullable=False, schema='public')


def downgrade():
    op.drop_column('users', 'fullname', schema='public')
