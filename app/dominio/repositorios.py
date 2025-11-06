"""
Interfaces de repositorios (Protocols).
Definen contratos sin implementación concreta.
"""
from typing import Protocol, Optional, List
from datetime import datetime, date
from uuid import UUID
from .entidades import (
    Usuario, Cita, Profesional, Prestacion, Alerta,
    SesionRegistro, Box, UsuarioSistema, HorarioProfesional,
    Bloqueo, AuditoriaEvento
)
from .valores import RUT, RangoTiempo


class IUsuarioRepo(Protocol):
    """Interfaz de repositorio para Usuario"""

    def obtener_por_rut(self, rut: RUT) -> Optional[Usuario]:
        """Busca usuario por RUT"""
        ...

    def obtener(self, id: UUID) -> Optional[Usuario]:
        """Obtiene usuario por ID"""
        ...

    def crear(self, usuario: Usuario) -> Usuario:
        """Crea nuevo usuario"""
        ...

    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza usuario existente"""
        ...

    def listar(self, activo: Optional[bool] = None, limit: int = 100, offset: int = 0) -> List[Usuario]:
        """Lista usuarios con filtro opcional de activo"""
        ...

    def eliminar(self, id: UUID) -> None:
        """Elimina usuario (soft delete)"""
        ...


class IProfesionalRepo(Protocol):
    """Interfaz de repositorio para Profesional"""

    def obtener(self, id: UUID) -> Optional[Profesional]:
        """Obtiene profesional por ID"""
        ...

    def crear(self, profesional: Profesional) -> Profesional:
        """Crea nuevo profesional"""
        ...

    def actualizar(self, profesional: Profesional) -> Profesional:
        """Actualiza profesional existente"""
        ...

    def listar(self, activo: Optional[bool] = None) -> List[Profesional]:
        """Lista profesionales con filtro opcional de activo"""
        ...

    def eliminar(self, id: UUID) -> None:
        """Elimina profesional (soft delete)"""
        ...


class IBoxRepo(Protocol):
    """Interfaz de repositorio para Box"""

    def obtener(self, id: UUID) -> Optional[Box]:
        """Obtiene box por ID"""
        ...

    def crear(self, box: Box) -> Box:
        """Crea nuevo box"""
        ...

    def actualizar(self, box: Box) -> Box:
        """Actualiza box existente"""
        ...

    def listar(self, activo: Optional[bool] = None) -> List[Box]:
        """Lista boxes con filtro opcional de activo"""
        ...

    def eliminar(self, id: UUID) -> None:
        """Elimina box (soft delete)"""
        ...


class IPrestacionRepo(Protocol):
    """Interfaz de repositorio para Prestacion"""

    def obtener(self, id: UUID) -> Optional[Prestacion]:
        """Obtiene prestacion por ID"""
        ...

    def crear(self, prestacion: Prestacion) -> Prestacion:
        """Crea nueva prestacion"""
        ...

    def actualizar(self, prestacion: Prestacion) -> Prestacion:
        """Actualiza prestacion existente"""
        ...

    def listar(self, habilitada: Optional[bool] = None) -> List[Prestacion]:
        """Lista prestaciones con filtro opcional de habilitada"""
        ...

    def eliminar(self, id: UUID) -> None:
        """Elimina prestacion (soft delete)"""
        ...


class IAgendaRepo(Protocol):
    """Interfaz de repositorio para Agenda (Citas y Bloqueos)"""

    def buscar_citas(
        self,
        profesional_id: Optional[UUID] = None,
        box_id: Optional[UUID] = None,
        usuario_id: Optional[UUID] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None
    ) -> List[Cita]:
        """Busca citas con filtros opcionales"""
        ...

    def crear_cita(self, cita: Cita) -> Cita:
        """Crea nueva cita"""
        ...

    def obtener_cita(self, cita_id: UUID) -> Optional[Cita]:
        """Obtiene cita por ID"""
        ...

    def actualizar_cita(self, cita: Cita) -> Cita:
        """Actualiza cita existente"""
        ...

    def actualizar_estado(self, cita_id: UUID, estado: str) -> None:
        """Actualiza estado de una cita"""
        ...

    def hay_solape(
        self,
        profesional_id: UUID,
        box_id: UUID,
        inicio: datetime,
        fin: datetime,
        excluir_cita_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica si existe solape temporal para profesional y box.
        Puede excluir una cita específica (útil para modificaciones).
        """
        ...

    def obtener_ultima_cita_usuario_prestacion(
        self,
        usuario_id: UUID,
        prestacion_id: UUID
    ) -> Optional[Cita]:
        """Obtiene última cita cumplida de usuario para prestación específica"""
        ...

    def crear_bloqueo(self, bloqueo: Bloqueo) -> Bloqueo:
        """Crea nuevo bloqueo"""
        ...

    def listar_bloqueos(
        self,
        profesional_id: Optional[UUID] = None,
        box_id: Optional[UUID] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> List[Bloqueo]:
        """Lista bloqueos con filtros opcionales"""
        ...


class ISesionesRepo(Protocol):
    """Interfaz de repositorio para Sesiones"""

    def crear_registro(self, sesion: SesionRegistro) -> SesionRegistro:
        """Crea nuevo registro de sesión"""
        ...

    def obtener_por_cita(self, cita_id: UUID) -> Optional[SesionRegistro]:
        """Obtiene registro de sesión por ID de cita"""
        ...

    def listar_por_usuario(self, usuario_id: UUID, limit: int = 100) -> List[SesionRegistro]:
        """Lista registros de sesión por usuario"""
        ...


class IAlertasRepo(Protocol):
    """Interfaz de repositorio para Alertas"""

    def crear(self, alerta: Alerta) -> Alerta:
        """Crea nueva alerta"""
        ...

    def listar_pendientes(
        self,
        usuario_id: Optional[UUID] = None,
        nivel: Optional[str] = None
    ) -> List[Alerta]:
        """Lista alertas no resueltas con filtros opcionales"""
        ...

    def marcar_resuelta(self, alerta_id: UUID) -> None:
        """Marca alerta como resuelta"""
        ...

    def obtener(self, alerta_id: UUID) -> Optional[Alerta]:
        """Obtiene alerta por ID"""
        ...


class IUsuarioSistemaRepo(Protocol):
    """Interfaz de repositorio para UsuarioSistema"""

    def obtener_por_email(self, email: str) -> Optional[UsuarioSistema]:
        """Busca usuario del sistema por email"""
        ...

    def obtener(self, id: UUID) -> Optional[UsuarioSistema]:
        """Obtiene usuario del sistema por ID"""
        ...

    def crear(self, usuario: UsuarioSistema) -> UsuarioSistema:
        """Crea nuevo usuario del sistema"""
        ...

    def actualizar(self, usuario: UsuarioSistema) -> UsuarioSistema:
        """Actualiza usuario del sistema existente"""
        ...

    def listar(self, activo: Optional[bool] = None) -> List[UsuarioSistema]:
        """Lista usuarios del sistema"""
        ...


class IHorarioProfesionalRepo(Protocol):
    """Interfaz de repositorio para HorarioProfesional"""

    def listar_por_profesional(self, profesional_id: UUID) -> List[HorarioProfesional]:
        """Lista horarios de un profesional"""
        ...

    def crear(self, horario: HorarioProfesional) -> HorarioProfesional:
        """Crea nuevo horario"""
        ...

    def actualizar(self, horario: HorarioProfesional) -> HorarioProfesional:
        """Actualiza horario existente"""
        ...

    def eliminar(self, id: UUID) -> None:
        """Elimina horario"""
        ...


class IAuditoriaRepo(Protocol):
    """Interfaz de repositorio para Auditoría"""

    def registrar_evento(self, evento: AuditoriaEvento) -> AuditoriaEvento:
        """Registra evento de auditoría"""
        ...

    def listar_eventos(
        self,
        usuario_id: Optional[UUID] = None,
        evento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditoriaEvento]:
        """Lista eventos de auditoría con filtros"""
        ...
