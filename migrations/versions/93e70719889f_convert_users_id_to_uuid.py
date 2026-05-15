"""convert users id to uuid

Revision ID: 93e70719889f
Revises: 92d70719889e
Create Date: 2026-05-08 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '93e70719889f'
down_revision = '92d70719889e'
branch_labels = None
depends_on = None


def upgrade():
    # Drop sequences and constraints that depend on the id column
    op.execute('ALTER TABLE public.audit_log DROP CONSTRAINT IF EXISTS audit_log_user_id_fkey')
    op.execute('ALTER TABLE public.clients DROP CONSTRAINT IF EXISTS clients_created_by_fkey')
    op.execute('ALTER TABLE public.loan_applications DROP CONSTRAINT IF EXISTS loan_applications_user_id_fkey')
    op.execute('ALTER TABLE public.score_history DROP CONSTRAINT IF EXISTS score_history_created_by_fkey')
    
    # Drop the id sequence if it exists
    op.execute('DROP SEQUENCE IF EXISTS public.users_id_seq CASCADE')
    
    # Convert the id column from INTEGER to UUID
    op.execute('ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT')
    op.execute('ALTER TABLE public.users ALTER COLUMN id TYPE UUID USING gen_random_uuid()')
    
    # Re-add foreign key constraints
    op.execute('ALTER TABLE public.audit_log ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL')
    op.execute('ALTER TABLE public.clients ADD CONSTRAINT clients_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL')
    op.execute('ALTER TABLE public.loan_applications ADD CONSTRAINT loan_applications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL')
    op.execute('ALTER TABLE public.score_history ADD CONSTRAINT score_history_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL')


def downgrade():
    # This is a destructive migration, so downgrade is not fully reversible
    pass
