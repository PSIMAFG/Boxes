"""
Router de usuarios (pacientes/beneficiarios).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import RequiereRecepcion, UsuarioActual
from app.infraestructura.repos.usuario_repo import UsuarioRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.usuario_service import UsuarioService
from app.aplicacion.dtos.usuario_dto import (
    UsuarioCreateDTO, UsuarioUpdateDTO, UsuarioResponseDTO
)

router = APIRouter()


def get_usuario_service(db: Session = Depends(get_db)) -> UsuarioService:
    """Dependency para obtener UsuarioService"""
    return UsuarioService(
        usuario_repo=UsuarioRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


@router.post("", response_model=UsuarioResponseDTO, status_code=201)
def crear_usuario(
    dto: UsuarioCreateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: UsuarioService = Depends(get_usuario_service)
):
    """Crear nuevo usuario"""
    try:
        return service.crear_usuario(dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{usuario_id}", response_model=UsuarioResponseDTO)
def obtener_usuario(
    usuario_id: UUID,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: UsuarioService = Depends(get_usuario_service)
):
    """Obtener usuario por ID"""
    resultado = service.obtener_usuario(usuario_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return resultado


@router.get("/rut/{rut}", response_model=UsuarioResponseDTO)
def obtener_por_rut(
    rut: str,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: UsuarioService = Depends(get_usuario_service)
):
    """Obtener usuario por RUT"""
    try:
        resultado = service.obtener_por_rut(rut)
        if not resultado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UsuarioResponseDTO])
def listar_usuarios(
    activo: Optional[bool] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: UsuarioService = Depends(get_usuario_service)
):
    """Listar usuarios con filtros"""
    return service.listar_usuarios(activo=activo, limit=limit, offset=offset)


@router.patch("/{usuario_id}", response_model=UsuarioResponseDTO)
def actualizar_usuario(
    usuario_id: UUID,
    dto: UsuarioUpdateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereRecepcion),
    service: UsuarioService = Depends(get_usuario_service)
):
    """Actualizar usuario"""
    try:
        return service.actualizar_usuario(usuario_id, dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
