"""
Router de alertas.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import RequiereRecepcion, UsuarioActual
from app.infraestructura.repos.alertas_repo import AlertasRepo
from app.infraestructura.repos.agenda_repo import AgendaRepo
from app.infraestructura.repos.usuario_repo import UsuarioRepo
from app.infraestructura.repos.prestacion_repo import PrestacionRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.alertas_service import AlertasService
from app.aplicacion.dtos.comunes_dto import AlertaResponseDTO

router = APIRouter()


def get_alertas_service(db: Session = Depends(get_db)) -> AlertasService:
    """Dependency para obtener AlertasService"""
    return AlertasService(
        alertas_repo=AlertasRepo(db),
        agenda_repo=AgendaRepo(db),
        usuario_repo=UsuarioRepo(db),
        prestacion_repo=PrestacionRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


@router.get("", response_model=List[AlertaResponseDTO])
def listar_alertas_pendientes(
    usuario_id: Optional[UUID] = Query(None),
    nivel: Optional[str] = Query(None),
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AlertasService = Depends(get_alertas_service)
):
    """Listar alertas pendientes con filtros"""
    return service.listar_alertas_pendientes(usuario_id=usuario_id, nivel=nivel)


@router.patch("/{alerta_id}/resolver", status_code=204)
def marcar_resuelta(
    alerta_id: UUID,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AlertasService = Depends(get_alertas_service)
):
    """Marcar alerta como resuelta"""
    service.marcar_resuelta(alerta_id, UUID(usuario_actual.user_id))


@router.post("/evaluar/{usuario_id}/{prestacion_id}", status_code=200)
def evaluar_control(
    usuario_id: UUID,
    prestacion_id: UUID,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: AlertasService = Depends(get_alertas_service)
):
    """Evaluar control de usuario para una prestación"""
    alerta = service.evaluar_control_usuario(usuario_id, prestacion_id)
    if alerta:
        return {"message": "Alerta creada", "nivel": alerta.nivel}
    return {"message": "Usuario bajo control"}
