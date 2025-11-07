"""Add box analytics fields and historial table

Revision ID: 002_box_analytics
Revises: 001_initial
Create Date: 2025-01-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_box_analytics'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar campos de analítica a boxes y crear tabla de historial"""

    # Agregar nuevos campos a tabla boxes
    op.add_column('boxes', sa.Column('piso', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('boxes', sa.Column('capacidad', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('boxes', sa.Column('equipamiento', sa.Text(), nullable=True))
    op.add_column('boxes', sa.Column('metros_cuadrados', sa.Integer(), nullable=True))

    # Agregar constraints a la tabla boxes
    op.create_check_constraint('check_piso', 'boxes', 'piso IN (1, 2)')
    op.create_check_constraint('check_capacidad', 'boxes', 'capacidad >= 1')

    # Crear tabla historial_boxes
    op.create_table(
        'historial_boxes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('box_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campo_modificado', sa.String(length=50), nullable=False),
        sa.Column('valor_anterior', sa.Text(), nullable=True),
        sa.Column('valor_nuevo', sa.Text(), nullable=False),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('modificado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['box_id'], ['boxes.id'], name='fk_historial_box_id'),
        sa.ForeignKeyConstraint(['modificado_por'], ['usuarios_sistema.id'], name='fk_historial_modificado_por'),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices para historial_boxes
    op.create_index('ix_historial_boxes_box_id', 'historial_boxes', ['box_id'])
    op.create_index('ix_historial_boxes_timestamp', 'historial_boxes', ['timestamp'])


def downgrade() -> None:
    """Revertir cambios de analítica"""

    # Eliminar tabla historial_boxes
    op.drop_index('ix_historial_boxes_timestamp', table_name='historial_boxes')
    op.drop_index('ix_historial_boxes_box_id', table_name='historial_boxes')
    op.drop_table('historial_boxes')

    # Eliminar constraints de boxes
    op.drop_constraint('check_capacidad', 'boxes', type_='check')
    op.drop_constraint('check_piso', 'boxes', type_='check')

    # Eliminar columnas de boxes
    op.drop_column('boxes', 'metros_cuadrados')
    op.drop_column('boxes', 'equipamiento')
    op.drop_column('boxes', 'capacidad')
    op.drop_column('boxes', 'piso')
