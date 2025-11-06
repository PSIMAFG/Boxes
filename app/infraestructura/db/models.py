"""
Modelos SQLAlchemy para persistencia.
Mapean entidades del dominio a tablas de base de datos.
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date, Time,
    ForeignKey, Text, JSON, Enum as SQLEnum, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid
import enum


Base = declarative_base()


class EstadoCita(enum.Enum):
    """Estados posibles de una cita"""
    PROGRAMADA = "programada"
    CONFIRMADA = "confirmada"
    CUMPLIDA = "cumplida"
    NO_ASISTIO = "no_asistio"
    CANCELADA = "cancelada"


class NivelAlerta(enum.Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARN = "warn"
    CRIT = "crit"


class RolUsuario(enum.Enum):
    """Roles de usuario del sistema"""
    ADMIN = "admin"
    PROFESIONAL = "profesional"
    RECEPCION = "recepcion"


class ValoracionSesion(enum.Enum):
    """Valoración de una sesión"""
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"


class ScopeBloqueo(enum.Enum):
    """Scope de bloqueo"""
    BOX = "box"
    PROFESIONAL = "profesional"


class UsuarioModel(Base):
    """Usuario del sistema clínico (paciente/beneficiario)"""
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rut = Column(String(12), unique=True, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    nivel_apoyo = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('nivel_apoyo IS NULL OR nivel_apoyo BETWEEN 1 AND 3', name='check_nivel_apoyo'),
    )


class ProfesionalModel(Base):
    """Terapeuta o médico que realiza prestaciones"""
    __tablename__ = "profesionales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    profesion = Column(String(100), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BoxModel(Base):
    """Sala o consultorio físico"""
    __tablename__ = "boxes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PrestacionModel(Base):
    """Tipo de servicio clínico"""
    __tablename__ = "prestaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
    periodicidad_dias = Column(Integer, nullable=False)
    tolerancia_dias = Column(Integer, nullable=False)
    habilitada = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CitaModel(Base):
    """Agendamiento de una sesión clínica"""
    __tablename__ = "citas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id"), nullable=False, index=True)
    prestacion_id = Column(UUID(as_uuid=True), ForeignKey("prestaciones.id"), nullable=False, index=True)
    box_id = Column(UUID(as_uuid=True), ForeignKey("boxes.id"), nullable=False, index=True)
    inicio = Column(DateTime, nullable=False, index=True)
    fin = Column(DateTime, nullable=False)
    estado = Column(SQLEnum(EstadoCita), default=EstadoCita.PROGRAMADA, nullable=False, index=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    usuario = relationship("UsuarioModel")
    profesional = relationship("ProfesionalModel")
    prestacion = relationship("PrestacionModel")
    box = relationship("BoxModel")


class SesionRegistroModel(Base):
    """Registro de resultado de una cita realizada"""
    __tablename__ = "sesiones_registros"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cita_id = Column(UUID(as_uuid=True), ForeignKey("citas.id"), nullable=False, unique=True)
    cumplida = Column(Boolean, nullable=False)
    valoracion = Column(SQLEnum(ValoracionSesion), nullable=True)
    notas = Column(Text, nullable=True)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    cita = relationship("CitaModel")
    creador = relationship("UsuarioSistemaModel")


class AlertaModel(Base):
    """Notificación de usuario fuera de control"""
    __tablename__ = "alertas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    prestacion_id = Column(UUID(as_uuid=True), ForeignKey("prestaciones.id"), nullable=False)
    nivel = Column(SQLEnum(NivelAlerta), nullable=False, index=True)
    motivo = Column(Text, nullable=False)
    fecha_objetivo = Column(Date, nullable=False)
    resuelta = Column(Boolean, default=False, nullable=False, index=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    resuelta_en = Column(DateTime, nullable=True)

    # Relationships
    usuario = relationship("UsuarioModel")
    prestacion = relationship("PrestacionModel")


class UsuarioSistemaModel(Base):
    """Usuario autenticado del sistema"""
    __tablename__ = "usuarios_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(SQLEnum(RolUsuario), nullable=False, index=True)
    activo = Column(Boolean, default=True, nullable=False)
    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id"), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profesional = relationship("ProfesionalModel")


class HorarioProfesionalModel(Base):
    """Disponibilidad semanal de un profesional"""
    __tablename__ = "horarios_profesionales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id"), nullable=False, index=True)
    dia_semana = Column(Integer, nullable=False)  # 0=Lunes, 6=Domingo
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    box_preferido_id = Column(UUID(as_uuid=True), ForeignKey("boxes.id"), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profesional = relationship("ProfesionalModel")
    box_preferido = relationship("BoxModel")

    # Constraints
    __table_args__ = (
        CheckConstraint('dia_semana BETWEEN 0 AND 6', name='check_dia_semana'),
        UniqueConstraint('profesional_id', 'dia_semana', name='uq_profesional_dia'),
    )


class BloqueoModel(Base):
    """Restricción temporal para profesional o box"""
    __tablename__ = "bloqueos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(SQLEnum(ScopeBloqueo), nullable=False)
    box_id = Column(UUID(as_uuid=True), ForeignKey("boxes.id"), nullable=True)
    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id"), nullable=True)
    inicio = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    motivo = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False)

    # Relationships
    box = relationship("BoxModel")
    profesional = relationship("ProfesionalModel")
    creador = relationship("UsuarioSistemaModel")


class AuditoriaEventoModel(Base):
    """Registro de auditoría de eventos del sistema"""
    __tablename__ = "auditoria_eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False, index=True)
    evento = Column(String(100), nullable=False, index=True)
    detalles = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_origen = Column(String(45), nullable=True)

    # Relationships
    usuario = relationship("UsuarioSistemaModel")
