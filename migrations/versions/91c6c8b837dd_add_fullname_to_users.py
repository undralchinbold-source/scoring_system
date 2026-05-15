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
    op.execute("""
        ALTER TABLE public.users
        ADD COLUMN IF NOT EXISTS fullname VARCHAR(255)
    """)
    op.execute("UPDATE public.users SET fullname = 'Unknown' WHERE fullname IS NULL")
    op.execute("""
        ALTER TABLE public.users
        ALTER COLUMN fullname SET NOT NULL
    """)


def downgrade():
    op.drop_column('users', 'fullname', schema='public')
