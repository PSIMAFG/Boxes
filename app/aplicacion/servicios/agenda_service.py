"""
Servicio de gestión de agenda (citas y bloqueos).
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from app.dominio.entidades import Cita, Bloqueo, AuditoriaEvento
from app.dominio.repositorios import (
    IAgendaRepo, IUsuarioRepo, IProfesionalRepo,
    IPrestacionRepo, IBoxRepo, IAuditoriaRepo
)
from app.dominio.reglas import validar_solapamiento
from app.aplicacion.dtos.cita_dto import (
    CitaCreateDTO, CitaResponseDTO, CitaUpdateDTO,
    SugerirSlotsRequestDTO, SlotSugeridoDTO
)
from app.aplicacion.dtos.comunes_dto import BloqueoCreateDTO, BloqueoResponseDTO


class AgendaService:
    """Servicio de gestión de agenda"""

    def __init__(
        self,
        agenda_repo: IAgendaRepo,
        usuario_repo: IUsuarioRepo,
        profesional_repo: IProfesionalRepo,
        prestacion_repo: IPrestacionRepo,
        box_repo: IBoxRepo,
        auditoria_repo: IAuditoriaRepo
    ):
        self.agenda_repo = agenda_repo
        self.usuario_repo = usuario_repo
        self.profesional_repo = profesional_repo
        self.prestacion_repo = prestacion_repo
        self.box_repo = box_repo
        self.auditoria_repo = auditoria_repo

    def crear_cita(self, dto: CitaCreateDTO, creado_por: UUID) -> CitaResponseDTO:
        """
        Crea una nueva cita con validaciones.

        Validaciones:
        - Usuario, profesional, prestacion y box existen
        - No hay solape de horario para profesional o box
        - Duración coincide con prestación

        Args:
            dto: Datos de la cita
            creado_por: ID del usuario que crea la cita

        Returns:
            Cita creada

        Raises:
            ValueError: Si hay errores de validación
        """
        # Validar que existan las entidades relacionadas
        usuario = self.usuario_repo.obtener(dto.usuario_id)
        if not usuario or not usuario.activo:
            raise ValueError(f"Usuario {dto.usuario_id} no encontrado o inactivo")

        profesional = self.profesional_repo.obtener(dto.profesional_id)
        if not profesional or not profesional.activo:
            raise ValueError(f"Profesional {dto.profesional_id} no encontrado o inactivo")

        prestacion = self.prestacion_repo.obtener(dto.prestacion_id)
        if not prestacion or not prestacion.habilitada:
            raise ValueError(f"Prestación {dto.prestacion_id} no encontrada o deshabilitada")

        box = self.box_repo.obtener(dto.box_id)
        if not box or not box.activo:
            raise ValueError(f"Box {dto.box_id} no encontrado o inactivo")

        # Validar que la duración sea correcta
        duracion = int((dto.fin - dto.inicio).total_seconds() / 60)
        if duracion != prestacion.duracion_minutos:
            raise ValueError(
                f"Duración incorrecta: esperada {prestacion.duracion_minutos} min, "
                f"recibida {duracion} min"
            )

        # Validar que no haya solapes
        hay_solape = self.agenda_repo.hay_solape(
            profesional_id=dto.profesional_id,
            box_id=dto.box_id,
            inicio=dto.inicio,
            fin=dto.fin
        )
        if hay_solape:
            raise ValueError("Existe solape de horario para el profesional o box")

        # Crear entidad
        cita = Cita(
            id=uuid4(),
            usuario_id=dto.usuario_id,
            profesional_id=dto.profesional_id,
            prestacion_id=dto.prestacion_id,
            box_id=dto.box_id,
            inicio=dto.inicio,
            fin=dto.fin,
            estado="programada",
            creado_en=datetime.utcnow(),
            actualizado_en=datetime.utcnow()
        )

        # Persistir
        cita = self.agenda_repo.crear_cita(cita)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=creado_por,
            evento="cita_creada",
            detalles={
                "cita_id": str(cita.id),
                "usuario_id": str(cita.usuario_id),
                "profesional_id": str(cita.profesional_id),
                "inicio": cita.inicio.isoformat()
            }
        ))

        return self._to_response_dto(cita)

    def obtener_cita(self, cita_id: UUID) -> Optional[CitaResponseDTO]:
        """Obtiene una cita por ID"""
        cita = self.agenda_repo.obtener_cita(cita_id)
        return self._to_response_dto(cita) if cita else None

    def listar_citas(
        self,
        profesional_id: Optional[UUID] = None,
        box_id: Optional[UUID] = None,
        usuario_id: Optional[UUID] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None
    ) -> List[CitaResponseDTO]:
        """Lista citas con filtros opcionales"""
        citas = self.agenda_repo.buscar_citas(
            profesional_id=profesional_id,
            box_id=box_id,
            usuario_id=usuario_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado
        )
        return [self._to_response_dto(c) for c in citas]

    def actualizar_cita(
        self,
        cita_id: UUID,
        dto: CitaUpdateDTO,
        actualizado_por: UUID
    ) -> CitaResponseDTO:
        """Actualiza una cita existente con validaciones"""
        cita = self.agenda_repo.obtener_cita(cita_id)
        if not cita:
            raise ValueError(f"Cita {cita_id} no encontrada")

        # Actualizar campos si vienen en el DTO
        if dto.usuario_id:
            cita.usuario_id = dto.usuario_id
        if dto.profesional_id:
            cita.profesional_id = dto.profesional_id
        if dto.prestacion_id:
            cita.prestacion_id = dto.prestacion_id
        if dto.box_id:
            cita.box_id = dto.box_id
        if dto.inicio:
            cita.inicio = dto.inicio
        if dto.fin:
            cita.fin = dto.fin
        if dto.estado:
            cita.estado = dto.estado

        # Validar solape si cambió horario
        if dto.inicio or dto.fin or dto.profesional_id or dto.box_id:
            hay_solape = self.agenda_repo.hay_solape(
                profesional_id=cita.profesional_id,
                box_id=cita.box_id,
                inicio=cita.inicio,
                fin=cita.fin,
                excluir_cita_id=cita_id
            )
            if hay_solape:
                raise ValueError("Existe solape de horario para el profesional o box")

        cita.actualizado_en = datetime.utcnow()

        # Persistir
        cita = self.agenda_repo.actualizar_cita(cita)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=actualizado_por,
            evento="cita_actualizada",
            detalles={"cita_id": str(cita_id)}
        ))

        return self._to_response_dto(cita)

    def cancelar_cita(self, cita_id: UUID, cancelado_por: UUID) -> None:
        """Cancela una cita"""
        cita = self.agenda_repo.obtener_cita(cita_id)
        if not cita:
            raise ValueError(f"Cita {cita_id} no encontrada")

        self.agenda_repo.actualizar_estado(cita_id, "cancelada")

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=cancelado_por,
            evento="cita_cancelada",
            detalles={"cita_id": str(cita_id)}
        ))

    def sugerir_slots(self, dto: SugerirSlotsRequestDTO) -> List[SlotSugeridoDTO]:
        """
        Sugiere slots disponibles para una cita.

        Algoritmo básico (sin ML):
        1. Genera slots cada 15 minutos en el rango solicitado
        2. Filtra slots que no tienen solapes
        3. Prioriza por boxes preferidos del profesional
        4. Opcionalmente aplica scoring ML

        Args:
            dto: Parámetros de búsqueda

        Returns:
            Lista de slots sugeridos ordenados por conveniencia
        """
        prestacion = self.prestacion_repo.obtener(dto.prestacion_id)
        if not prestacion:
            raise ValueError(f"Prestación {dto.prestacion_id} no encontrada")

        slots_disponibles = []
        duracion = timedelta(minutes=prestacion.duracion_minutos)

        # Generar slots candidatos cada 15 minutos
        slot_inicio = dto.fecha_desde
        while slot_inicio + duracion <= dto.fecha_hasta:
            slot_fin = slot_inicio + duracion

            # Buscar boxes disponibles para este slot
            boxes = self.box_repo.listar(activo=True)
            for box in boxes:
                # Verificar si hay solape
                hay_solape = self.agenda_repo.hay_solape(
                    profesional_id=dto.profesional_id,
                    box_id=box.id,
                    inicio=slot_inicio,
                    fin=slot_fin
                )

                if not hay_solape:
                    slot = SlotSugeridoDTO(
                        inicio=slot_inicio,
                        fin=slot_fin,
                        box_id=box.id,
                        box_nombre=box.nombre,
                        score=None,
                        razones=["Horario disponible"]
                    )
                    slots_disponibles.append(slot)

            slot_inicio += timedelta(minutes=15)

        # Limitar a primeros 20 slots
        return slots_disponibles[:20]

    def crear_bloqueo(self, dto: BloqueoCreateDTO, creado_por: UUID) -> BloqueoResponseDTO:
        """Crea un bloqueo de horario"""
        bloqueo = Bloqueo(
            id=uuid4(),
            scope=dto.scope,
            box_id=dto.box_id,
            profesional_id=dto.profesional_id,
            inicio=dto.inicio,
            fin=dto.fin,
            motivo=dto.motivo,
            creado_en=datetime.utcnow(),
            creado_por=creado_por
        )

        bloqueo = self.agenda_repo.crear_bloqueo(bloqueo)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=creado_por,
            evento="bloqueo_creado",
            detalles={
                "bloqueo_id": str(bloqueo.id),
                "scope": bloqueo.scope,
                "inicio": bloqueo.inicio.isoformat()
            }
        ))

        return self._bloqueo_to_response(bloqueo)

    def _to_response_dto(self, cita: Cita) -> CitaResponseDTO:
        """Convierte entidad Cita a DTO de respuesta"""
        return CitaResponseDTO(
            id=cita.id,
            usuario_id=cita.usuario_id,
            profesional_id=cita.profesional_id,
            prestacion_id=cita.prestacion_id,
            box_id=cita.box_id,
            inicio=cita.inicio,
            fin=cita.fin,
            estado=cita.estado,
            duracion_minutos=cita.duracion_minutos(),
            creado_en=cita.creado_en,
            actualizado_en=cita.actualizado_en
        )

    def _bloqueo_to_response(self, bloqueo: Bloqueo) -> BloqueoResponseDTO:
        """Convierte entidad Bloqueo a DTO de respuesta"""
        return BloqueoResponseDTO(
            id=bloqueo.id,
            scope=bloqueo.scope,
            box_id=bloqueo.box_id,
            profesional_id=bloqueo.profesional_id,
            inicio=bloqueo.inicio,
            fin=bloqueo.fin,
            motivo=bloqueo.motivo,
            creado_en=bloqueo.creado_en,
            creado_por=bloqueo.creado_por
        )
