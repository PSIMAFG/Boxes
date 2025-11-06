"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables"""
    # Usuarios
    op.create_table(
        'usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rut', sa.String(12), unique=True, nullable=False, index=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=False),
        sa.Column('nivel_apoyo', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False),
        sa.CheckConstraint('nivel_apoyo IS NULL OR nivel_apoyo BETWEEN 1 AND 3', name='check_nivel_apoyo')
    )

    # Profesionales
    op.create_table(
        'profesionales',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('profesion', sa.String(100), nullable=False),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False)
    )

    # Boxes
    op.create_table(
        'boxes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('ubicacion', sa.String(255), nullable=False),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False)
    )

    # Prestaciones
    op.create_table(
        'prestaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('duracion_minutos', sa.Integer(), nullable=False),
        sa.Column('periodicidad_dias', sa.Integer(), nullable=False),
        sa.Column('tolerancia_dias', sa.Integer(), nullable=False),
        sa.Column('habilitada', sa.Boolean(), default=True, nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False)
    )

    # Usuarios Sistema
    op.create_table(
        'usuarios_sistema',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('rol', sa.Enum('ADMIN', 'PROFESIONAL', 'RECEPCION', name='rolusuario'), nullable=False, index=True),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id'), nullable=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False)
    )

    # Citas
    op.create_table(
        'citas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False, index=True),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id'), nullable=False, index=True),
        sa.Column('prestacion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('prestaciones.id'), nullable=False, index=True),
        sa.Column('box_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('boxes.id'), nullable=False, index=True),
        sa.Column('inicio', sa.DateTime(), nullable=False, index=True),
        sa.Column('fin', sa.DateTime(), nullable=False),
        sa.Column('estado', sa.Enum('PROGRAMADA', 'CONFIRMADA', 'CUMPLIDA', 'NO_ASISTIO', 'CANCELADA', name='estadocita'), nullable=False, index=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False)
    )

    # Sesiones Registros
    op.create_table(
        'sesiones_registros',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cita_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('citas.id'), nullable=False, unique=True),
        sa.Column('cumplida', sa.Boolean(), nullable=False),
        sa.Column('valoracion', sa.Enum('POSITIVO', 'NEUTRO', 'NEGATIVO', name='valoracionsesion'), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios_sistema.id'), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False)
    )

    # Alertas
    op.create_table(
        'alertas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), nullable=False, index=True),
        sa.Column('prestacion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('prestaciones.id'), nullable=False),
        sa.Column('nivel', sa.Enum('INFO', 'WARN', 'CRIT', name='nivelalerta'), nullable=False, index=True),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('fecha_objetivo', sa.Date(), nullable=False),
        sa.Column('resuelta', sa.Boolean(), default=False, nullable=False, index=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('resuelta_en', sa.DateTime(), nullable=True)
    )

    # Horarios Profesionales
    op.create_table(
        'horarios_profesionales',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id'), nullable=False, index=True),
        sa.Column('dia_semana', sa.Integer(), nullable=False),
        sa.Column('hora_inicio', sa.Time(), nullable=False),
        sa.Column('hora_fin', sa.Time(), nullable=False),
        sa.Column('box_preferido_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('boxes.id'), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True, nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False),
        sa.CheckConstraint('dia_semana BETWEEN 0 AND 6', name='check_dia_semana'),
        sa.UniqueConstraint('profesional_id', 'dia_semana', name='uq_profesional_dia')
    )

    # Bloqueos
    op.create_table(
        'bloqueos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('scope', sa.Enum('BOX', 'PROFESIONAL', name='scopebloqueo'), nullable=False),
        sa.Column('box_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('boxes.id'), nullable=True),
        sa.Column('profesional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('profesionales.id'), nullable=True),
        sa.Column('inicio', sa.DateTime(), nullable=False),
        sa.Column('fin', sa.DateTime(), nullable=False),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios_sistema.id'), nullable=False)
    )

    # Auditoría Eventos
    op.create_table(
        'auditoria_eventos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('usuarios_sistema.id'), nullable=False, index=True),
        sa.Column('evento', sa.String(100), nullable=False, index=True),
        sa.Column('detalles', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('ip_origen', sa.String(45), nullable=True)
    )


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('auditoria_eventos')
    op.drop_table('bloqueos')
    op.drop_table('horarios_profesionales')
    op.drop_table('alertas')
    op.drop_table('sesiones_registros')
    op.drop_table('citas')
    op.drop_table('usuarios_sistema')
    op.drop_table('prestaciones')
    op.drop_table('boxes')
    op.drop_table('profesionales')
    op.drop_table('usuarios')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS rolusuario')
    op.execute('DROP TYPE IF EXISTS estadocita')
    op.execute('DROP TYPE IF EXISTS valoracionsesion')
    op.execute('DROP TYPE IF EXISTS nivelalerta')
    op.execute('DROP TYPE IF EXISTS scopebloqueo')
