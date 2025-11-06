"""
Entidades del dominio con invariantes.
Objetos con identidad única que contienen lógica de negocio.
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, Literal
from uuid import UUID, uuid4
from .valores import RUT, Periodicidad


@dataclass
class Usuario:
    """
    Usuario del sistema clínico (paciente/beneficiario).

    Invariantes:
    - RUT debe ser válido según módulo 11
    - Nombre mínimo 3 caracteres
    - Nivel de apoyo entre 1-3 o None
    """
    id: UUID = field(default_factory=uuid4)
    rut: RUT = field(default=None)
    nombre: str = ""
    fecha_nacimiento: date = field(default_factory=date.today)
    nivel_apoyo: Optional[Literal[1, 2, 3]] = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.rut and not self.rut.es_valido():
            raise ValueError(f"RUT inválido: {self.rut.valor}")
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise ValueError("Nombre debe tener al menos 3 caracteres")

    def edad(self) -> int:
        """Calcula edad actual en años"""
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def requiere_apoyo_especial(self) -> bool:
        """Indica si usuario requiere nivel de apoyo 2 o 3"""
        return self.nivel_apoyo in [2, 3]


@dataclass
class Profesional:
    """Terapeuta o médico que realiza prestaciones"""
    id: UUID = field(default_factory=uuid4)
    nombre: str = ""
    profesion: str = ""
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise ValueError("Nombre debe tener al menos 3 caracteres")
        if not self.profesion or len(self.profesion.strip()) < 3:
            raise ValueError("Profesión debe tener al menos 3 caracteres")


@dataclass
class Box:
    """Sala o consultorio físico"""
    id: UUID = field(default_factory=uuid4)
    nombre: str = ""
    ubicacion: str = ""
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError("Nombre de box debe tener al menos 2 caracteres")


@dataclass
class Prestacion:
    """
    Tipo de servicio clínico.
    Incluye periodicidad para control de tratamientos recurrentes.
    """
    id: UUID = field(default_factory=uuid4)
    nombre: str = ""
    duracion_minutos: int = 30
    periodicidad_dias: int = 30
    tolerancia_dias: int = 7
    habilitada: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.duracion_minutos <= 0 or self.duracion_minutos > 480:
            raise ValueError("Duración debe estar entre 1 y 480 minutos")
        if self.periodicidad_dias <= 0:
            raise ValueError("Periodicidad debe ser mayor a 0 días")
        if self.tolerancia_dias < 0:
            raise ValueError("Tolerancia no puede ser negativa")

    def periodicidad(self) -> Periodicidad:
        """Retorna value object de periodicidad"""
        return Periodicidad(
            periodicidad_dias=self.periodicidad_dias,
            tolerancia_dias=self.tolerancia_dias
        )

    def es_recurrente(self) -> bool:
        """Indica si la prestación requiere seguimiento periódico"""
        return self.periodicidad_dias > 0


@dataclass
class Cita:
    """
    Agendamiento de una sesión clínica.

    Invariantes:
    - fin debe ser posterior a inicio
    - inicio no puede ser en el pasado
    - estado debe ser válido
    """
    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID = field(default_factory=uuid4)
    profesional_id: UUID = field(default_factory=uuid4)
    prestacion_id: UUID = field(default_factory=uuid4)
    box_id: UUID = field(default_factory=uuid4)
    inicio: datetime = field(default_factory=datetime.utcnow)
    fin: datetime = field(default_factory=datetime.utcnow)
    estado: Literal["programada", "confirmada", "cumplida", "no_asistio", "cancelada"] = "programada"
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("inicio debe ser anterior a fin")
        # Permitir citas en el pasado para datos históricos
        # if self.inicio < datetime.utcnow():
        #     raise ValueError("No se puede crear cita en el pasado")

    def duracion_minutos(self) -> int:
        """Retorna duración de la cita en minutos"""
        return int((self.fin - self.inicio).total_seconds() / 60)

    def esta_pendiente(self) -> bool:
        """Indica si cita está programada o confirmada"""
        return self.estado in ["programada", "confirmada"]

    def fue_cumplida(self) -> bool:
        """Indica si cita fue realizada exitosamente"""
        return self.estado == "cumplida"

    def puede_registrarse(self) -> bool:
        """Indica si se puede registrar resultado de sesión"""
        return self.estado in ["programada", "confirmada"]


@dataclass
class SesionRegistro:
    """Registro de resultado de una cita realizada"""
    id: UUID = field(default_factory=uuid4)
    cita_id: UUID = field(default_factory=uuid4)
    cumplida: bool = False
    valoracion: Optional[Literal["positivo", "neutro", "negativo"]] = None
    notas: Optional[str] = None
    creado_por: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alerta:
    """
    Notificación de usuario fuera de control.

    Nivel info: preventivo (7 días antes)
    Nivel warn: en ventana sin cita programada
    Nivel crit: fuera de ventana de tolerancia
    """
    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID = field(default_factory=uuid4)
    prestacion_id: UUID = field(default_factory=uuid4)
    nivel: Literal["info", "warn", "crit"] = "info"
    motivo: str = ""
    fecha_objetivo: date = field(default_factory=date.today)
    resuelta: bool = False
    creado_en: datetime = field(default_factory=datetime.utcnow)
    resuelta_en: Optional[datetime] = None

    def es_critica(self) -> bool:
        """Indica si alerta es crítica y requiere acción inmediata"""
        return self.nivel == "crit"


@dataclass
class UsuarioSistema:
    """Usuario autenticado del sistema"""
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    password_hash: str = ""
    rol: Literal["admin", "profesional", "recepcion"] = "recepcion"
    activo: bool = True
    profesional_id: Optional[UUID] = None  # Si rol=profesional, link al profesional
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def es_admin(self) -> bool:
        """Indica si el usuario es administrador"""
        return self.rol == "admin"

    def es_profesional(self) -> bool:
        """Indica si el usuario es profesional"""
        return self.rol == "profesional"

    def es_recepcion(self) -> bool:
        """Indica si el usuario es recepcionista"""
        return self.rol == "recepcion"


@dataclass
class HorarioProfesional:
    """Disponibilidad semanal de un profesional"""
    id: UUID = field(default_factory=uuid4)
    profesional_id: UUID = field(default_factory=uuid4)
    dia_semana: int = 0  # 0=Lunes, 6=Domingo
    hora_inicio: time = time(9, 0)
    hora_fin: time = time(18, 0)
    box_preferido_id: Optional[UUID] = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not 0 <= self.dia_semana <= 6:
            raise ValueError("dia_semana debe estar entre 0 (lunes) y 6 (domingo)")
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("hora_inicio debe ser < hora_fin")

    def duracion_minutos(self) -> int:
        """Retorna duración del horario en minutos"""
        delta = datetime.combine(datetime.today(), self.hora_fin) - \
                datetime.combine(datetime.today(), self.hora_inicio)
        return int(delta.total_seconds() / 60)


@dataclass
class Bloqueo:
    """Restricción temporal para profesional o box"""
    id: UUID = field(default_factory=uuid4)
    scope: Literal["box", "profesional"] = "profesional"
    box_id: Optional[UUID] = None
    profesional_id: Optional[UUID] = None
    inicio: datetime = field(default_factory=datetime.utcnow)
    fin: datetime = field(default_factory=datetime.utcnow)
    motivo: str = ""
    creado_en: datetime = field(default_factory=datetime.utcnow)
    creado_por: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("inicio debe ser anterior a fin")
        if self.scope == "box" and not self.box_id:
            raise ValueError("box_id requerido cuando scope='box'")
        if self.scope == "profesional" and not self.profesional_id:
            raise ValueError("profesional_id requerido cuando scope='profesional'")


@dataclass
class AuditoriaEvento:
    """Registro de auditoría de eventos del sistema"""
    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID = field(default_factory=uuid4)
    evento: str = ""
    detalles: Optional[dict] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_origen: Optional[str] = None
