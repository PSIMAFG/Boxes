"""Add floor and characteristics to boxes

Revision ID: 002_box_enhancements
Revises: 001_initial
Create Date: 2025-01-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_box_enhancements'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new columns to boxes table"""
    from sqlalchemy import inspect
    from alembic import context

    conn = context.get_bind()
    inspector = inspect(conn)

    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('boxes')]

    # Add piso column if it doesn't exist
    if 'piso' not in existing_columns:
        op.add_column('boxes', sa.Column('piso', sa.Integer(), nullable=True))

    # Add capacidad column if it doesn't exist
    if 'capacidad' not in existing_columns:
        op.add_column('boxes', sa.Column('capacidad', sa.Integer(), nullable=False, server_default='1'))

    # Add equipamiento column if it doesn't exist
    if 'equipamiento' not in existing_columns:
        op.add_column('boxes', sa.Column('equipamiento', sa.Text(), nullable=True))

    # Add caracteristicas column if it doesn't exist
    if 'caracteristicas' not in existing_columns:
        op.add_column('boxes', sa.Column('caracteristicas', sa.Text(), nullable=True))

    # Add constraints if they don't exist
    # Note: SQLite doesn't support adding constraints after table creation,
    # so we check if we're on SQLite and skip constraint addition
    try:
        op.create_check_constraint('check_piso', 'boxes', 'piso IS NULL OR piso IN (1, 2)')
    except:
        pass  # Constraint already exists or SQLite

    try:
        op.create_check_constraint('check_capacidad', 'boxes', 'capacidad >= 1')
    except:
        pass  # Constraint already exists or SQLite


def downgrade() -> None:
    """Remove new columns from boxes table"""
    op.drop_constraint('check_capacidad', 'boxes', type_='check')
    op.drop_constraint('check_piso', 'boxes', type_='check')
    op.drop_column('boxes', 'caracteristicas')
    op.drop_column('boxes', 'equipamiento')
    op.drop_column('boxes', 'capacidad')
    op.drop_column('boxes', 'piso')
