"""
Servicio de gestión de alertas y control de periodicidad.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from app.dominio.entidades import Alerta, AuditoriaEvento
from app.dominio.repositorios import (
    IAlertasRepo, IAgendaRepo, IUsuarioRepo, IPrestacionRepo, IAuditoriaRepo
)
from app.dominio.reglas import esta_en_ventana_tolerancia, calcular_fecha_objetivo_proxima
from app.aplicacion.dtos.comunes_dto import AlertaResponseDTO


class AlertasService:
    """Servicio de gestión de alertas"""

    def __init__(
        self,
        alertas_repo: IAlertasRepo,
        agenda_repo: IAgendaRepo,
        usuario_repo: IUsuarioRepo,
        prestacion_repo: IPrestacionRepo,
        auditoria_repo: IAuditoriaRepo
    ):
        self.alertas_repo = alertas_repo
        self.agenda_repo = agenda_repo
        self.usuario_repo = usuario_repo
        self.prestacion_repo = prestacion_repo
        self.auditoria_repo = auditoria_repo

    def evaluar_control_usuario(self, usuario_id: UUID, prestacion_id: UUID) -> Optional[Alerta]:
        """
        Evalúa si un usuario está bajo control para una prestación.
        Crea alerta si está fuera de control.

        Lógica:
        1. Busca última cita cumplida del usuario para la prestación
        2. Calcula fecha objetivo según periodicidad
        3. Busca si hay próxima cita programada
        4. Si no hay próxima cita y está fuera de ventana: crea alerta CRIT
        5. Si hay próxima cita pero fuera de ventana: crea alerta WARN
        6. Si está próximo a salir de ventana (7 días): crea alerta INFO

        Args:
            usuario_id: ID del usuario
            prestacion_id: ID de la prestación

        Returns:
            Alerta creada si corresponde, None si está bajo control
        """
        # Obtener prestación para periodicidad
        prestacion = self.prestacion_repo.obtener(prestacion_id)
        if not prestacion:
            return None

        # Obtener última cita cumplida
        ultima_cita = self.agenda_repo.obtener_ultima_cita_usuario_prestacion(
            usuario_id, prestacion_id
        )

        # Calcular fecha objetivo
        fecha_objetivo = calcular_fecha_objetivo_proxima(
            ultima_cita.fin if ultima_cita else None,
            prestacion.periodicidad_dias
        )

        # Buscar próxima cita programada o confirmada
        proxima_cita = self.agenda_repo.buscar_citas(
            usuario_id=usuario_id,
            fecha_desde=datetime.utcnow(),
            estado="programada"
        ) or self.agenda_repo.buscar_citas(
            usuario_id=usuario_id,
            fecha_desde=datetime.utcnow(),
            estado="confirmada"
        )

        # Si no hay próxima cita
        if not proxima_cita:
            # Verificar si está fuera de ventana
            hoy = datetime.utcnow()
            if not esta_en_ventana_tolerancia(
                hoy, fecha_objetivo, prestacion.tolerancia_dias
            ):
                # Alerta crítica: sin cita y fuera de ventana
                alerta = Alerta(
                    id=uuid4(),
                    usuario_id=usuario_id,
                    prestacion_id=prestacion_id,
                    nivel="crit",
                    motivo=f"Usuario sin próxima cita y fuera de ventana de tolerancia",
                    fecha_objetivo=fecha_objetivo.date(),
                    resuelta=False,
                    creado_en=datetime.utcnow()
                )
                return self.alertas_repo.crear(alerta)

            # Verificar si está próximo a salir de ventana (7 días)
            dias_hasta_objetivo = (fecha_objetivo.date() - hoy.date()).days
            if 0 <= dias_hasta_objetivo <= 7:
                # Alerta informativa
                alerta = Alerta(
                    id=uuid4(),
                    usuario_id=usuario_id,
                    prestacion_id=prestacion_id,
                    nivel="info",
                    motivo=f"Usuario próximo a fecha objetivo ({dias_hasta_objetivo} días)",
                    fecha_objetivo=fecha_objetivo.date(),
                    resuelta=False,
                    creado_en=datetime.utcnow()
                )
                return self.alertas_repo.crear(alerta)

        return None

    def listar_alertas_pendientes(
        self,
        usuario_id: Optional[UUID] = None,
        nivel: Optional[str] = None
    ) -> List[AlertaResponseDTO]:
        """Lista alertas no resueltas con filtros"""
        alertas = self.alertas_repo.listar_pendientes(usuario_id=usuario_id, nivel=nivel)
        return [self._to_response_dto(a) for a in alertas]

    def marcar_resuelta(self, alerta_id: UUID, resuelto_por: UUID) -> None:
        """Marca una alerta como resuelta"""
        self.alertas_repo.marcar_resuelta(alerta_id)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=resuelto_por,
            evento="alerta_resuelta",
            detalles={"alerta_id": str(alerta_id)}
        ))

    def _to_response_dto(self, alerta: Alerta) -> AlertaResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return AlertaResponseDTO(
            id=alerta.id,
            usuario_id=alerta.usuario_id,
            prestacion_id=alerta.prestacion_id,
            nivel=alerta.nivel,
            motivo=alerta.motivo,
            fecha_objetivo=alerta.fecha_objetivo,
            resuelta=alerta.resuelta,
            creado_en=alerta.creado_en,
            resuelta_en=alerta.resuelta_en
        )
