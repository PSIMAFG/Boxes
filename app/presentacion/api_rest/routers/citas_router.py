"""
Router de citas y agenda.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import RequiereRecepcion, UsuarioActual
from app.infraestructura.repos.agenda_repo import AgendaRepo
from app.infraestructura.repos.usuario_repo import UsuarioRepo
from app.infraestructura.repos.profesional_repo import ProfesionalRepo
from app.infraestructura.repos.prestacion_repo import PrestacionRepo
from app.infraestructura.repos.box_repo import BoxRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.agenda_service import AgendaService
from app.aplicacion.dtos.cita_dto import (
    CitaCreateDTO, CitaResponseDTO, CitaUpdateDTO,
    SugerirSlotsRequestDTO, SlotSugeridoDTO
)
from app.aplicacion.dtos.comunes_dto import BloqueoCreateDTO, BloqueoResponseDTO

router = APIRouter()


def get_agenda_service(db: Session = Depends(get_db)) -> AgendaService:
    """Dependency para obtener AgendaService"""
    return AgendaService(
        agenda_repo=AgendaRepo(db),
        usuario_repo=UsuarioRepo(db),
        profesional_repo=ProfesionalRepo(db),
        prestacion_repo=PrestacionRepo(db),
        box_repo=BoxRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


@router.post("", response_model=CitaResponseDTO, status_code=201)
def crear_cita(
    dto: CitaCreateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Crear nueva cita"""
    try:
        return service.crear_cita(dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{cita_id}", response_model=CitaResponseDTO)
def obtener_cita(
    cita_id: UUID,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Obtener cita por ID"""
    resultado = service.obtener_cita(cita_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return resultado


@router.get("", response_model=List[CitaResponseDTO])
def listar_citas(
    profesional_id: Optional[UUID] = Query(None),
    box_id: Optional[UUID] = Query(None),
    usuario_id: Optional[UUID] = Query(None),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    estado: Optional[str] = Query(None),
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Listar citas con filtros"""
    return service.listar_citas(
        profesional_id=profesional_id,
        box_id=box_id,
        usuario_id=usuario_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        estado=estado
    )


@router.patch("/{cita_id}", response_model=CitaResponseDTO)
def actualizar_cita(
    cita_id: UUID,
    dto: CitaUpdateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Actualizar cita"""
    try:
        return service.actualizar_cita(cita_id, dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cita_id}", status_code=204)
def cancelar_cita(
    cita_id: UUID,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Cancelar cita"""
    try:
        service.cancelar_cita(cita_id, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sugerir-slots", response_model=List[SlotSugeridoDTO])
def sugerir_slots(
    dto: SugerirSlotsRequestDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Sugerir slots disponibles para una cita"""
    try:
        return service.sugerir_slots(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bloqueos", response_model=BloqueoResponseDTO, status_code=201)
def crear_bloqueo(
    dto: BloqueoCreateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AgendaService = Depends(get_agenda_service)
):
    """Crear bloqueo de horario"""
    try:
        return service.crear_bloqueo(dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
