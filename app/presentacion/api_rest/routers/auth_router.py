"""
Router de autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import obtener_usuario_actual, RequiereAdmin, UsuarioActual
from app.infraestructura.repos.usuario_sistema_repo import UsuarioSistemaRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.auth_service import AuthService
from app.aplicacion.dtos.auth_dto import (
    LoginRequestDTO, LoginResponseDTO,
    UsuarioSistemaCreateDTO, UsuarioSistemaResponseDTO
)

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obtener AuthService"""
    return AuthService(
        usuario_sistema_repo=UsuarioSistemaRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


@router.post("/login", response_model=LoginResponseDTO)
def login(dto: LoginRequestDTO, service: AuthService = Depends(get_auth_service)):
    """Autenticar y obtener JWT token"""
    try:
        return service.login(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UsuarioSistemaResponseDTO)
def get_me(
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),
    service: AuthService = Depends(get_auth_service)
):
    """Obtener información del usuario autenticado actual"""
    from uuid import UUID
    resultado = service.obtener_usuario(UUID(usuario_actual.user_id))
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return resultado


@router.post("/usuarios-sistema", response_model=UsuarioSistemaResponseDTO)
def crear_usuario_sistema(
    dto: UsuarioSistemaCreateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),
    service: AuthService = Depends(get_auth_service)
):
    """Crear nuevo usuario del sistema (solo admins)"""
    try:
        from uuid import UUID
        return service.crear_usuario_sistema(dto, UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
