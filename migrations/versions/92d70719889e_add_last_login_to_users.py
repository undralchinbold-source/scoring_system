"""add last_login to users

Revision ID: 92d70719889e
Revises: 91c6c8b837dd
Create Date: 2026-05-08 19:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92d70719889e'
down_revision = '91c6c8b837dd'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE public.users
        ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ
    """)


def downgrade():
    op.drop_column('users', 'last_login', schema='public')
