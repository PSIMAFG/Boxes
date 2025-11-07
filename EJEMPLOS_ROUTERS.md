# 🛣️ EJEMPLOS DE ROUTERS (API REST)

**Framework:** FastAPI
**Documentación:** OpenAPI/Swagger automática

---

## [6] ROUTERS DE AUTENTICACIÓN

### 6.1 Router de Auth Completo

```python
# app/presentacion/api_rest/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import obtener_usuario_actual, RequiereAdmin, UsuarioActual
from app.infraestructura.repos.usuario_sistema_repo import UsuarioSistemaRepo
from app.infraestructura.repos.refresh_token_repo import RefreshTokenRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.auth_service import AuthService
from app.aplicacion.dtos.auth_dto import (
    RegistroRequestDTO, LoginRequestDTO, LoginResponseDTO,
    RefreshTokenRequestDTO, AprobarUsuarioDTO,
    UsuarioSistemaResponseDTO, UsuarioPendienteDTO
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obtener AuthService"""
    return AuthService(
        usuario_sistema_repo=UsuarioSistemaRepo(db),
        refresh_token_repo=RefreshTokenRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


# ============================================
# ENDPOINTS PÚBLICOS
# ============================================

@router.post("/registro", response_model=UsuarioSistemaResponseDTO, status_code=status.HTTP_201_CREATED)
def registrar_usuario(
    dto: RegistroRequestDTO,
    service: AuthService = Depends(get_auth_service)
):
    """
    🔓 **Público** - Registrar nuevo usuario.

    El usuario queda en estado PENDIENTE hasta que un admin lo apruebe.
    """
    try:
        return service.registrar_usuario(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponseDTO)
def login(
    dto: LoginRequestDTO,
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    """
    🔓 **Público** - Autenticarse con email y password.

    Retorna:
    - access_token: JWT de corta duración (15 min)
    - refresh_token: Token de larga duración (7 días)
    """
    try:
        ip_origen = request.client.host if request.client else None
        return service.login(dto, ip_origen=ip_origen)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=dict)
def refresh_token(
    dto: RefreshTokenRequestDTO,
    service: AuthService = Depends(get_auth_service)
):
    """
    🔓 **Público** - Renovar access token usando refresh token.
    """
    try:
        return service.refresh_access_token(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# ============================================
# ENDPOINTS PROTEGIDOS
# ============================================

@router.get("/me", response_model=UsuarioSistemaResponseDTO)
def obtener_usuario_actual_info(
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),
    service: AuthService = Depends(get_auth_service)
):
    """
    🔒 **Autenticado** - Obtener información del usuario actual.
    """
    usuario = service.usuario_repo.obtener_por_id(UUID(usuario_actual.user_id))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioSistemaResponseDTO.model_validate(usuario)


# ============================================
# ENDPOINTS SOLO ADMIN
# ============================================

@router.get("/usuarios-pendientes", response_model=list[UsuarioPendienteDTO])
def listar_usuarios_pendientes(
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),
    service: AuthService = Depends(get_auth_service)
):
    """
    🔒 **Solo Admin** - Listar usuarios pendientes de aprobación.
    """
    return service.listar_usuarios_pendientes()


@router.post("/aprobar/{usuario_id}", response_model=UsuarioSistemaResponseDTO)
def aprobar_usuario(
    usuario_id: str,
    dto: AprobarUsuarioDTO,
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),
    service: AuthService = Depends(get_auth_service)
):
    """
    🔒 **Solo Admin** - Aprobar usuario pendiente y asignar rol.

    Roles disponibles:
    - admin: Acceso total al sistema
    - profesional: Puede registrar atenciones y crear pacientes
    - administrativo: Solo lectura

    Si rol = profesional, debe proporcionar profesional_id.
    """
    try:
        return service.aprobar_usuario(
            usuario_id=UUID(usuario_id),
            dto=dto,
            aprobado_por_id=UUID(usuario_actual.user_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/rechazar/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def rechazar_usuario(
    usuario_id: str,
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),
    service: AuthService = Depends(get_auth_service)
):
    """
    🔒 **Solo Admin** - Rechazar y eliminar usuario pendiente.
    """
    try:
        service.rechazar_usuario(
            usuario_id=UUID(usuario_id),
            rechazado_por_id=UUID(usuario_actual.user_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/logout")
def logout(
    refresh_token: str,
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),
    service: AuthService = Depends(get_auth_service)
):
    """
    🔒 **Autenticado** - Cerrar sesión (revocar refresh token).
    """
    try:
        service.refresh_repo.revocar_por_token(refresh_token)
        return {"message": "Sesión cerrada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 6.2 Router de Pacientes (con RBAC)

```python
# app/presentacion/api_rest/routers/pacientes_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.rbac import (
    obtener_usuario_actual, RequiereAdmin, RequiereProfesional, UsuarioActual
)
from app.infraestructura.repos.paciente_repo import PacienteRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.servicios.paciente_service import PacienteService
from app.aplicacion.dtos.paciente_dto import (
    PacienteCreateDTO, PacienteResponseDTO, PacienteListItemDTO
)

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def get_paciente_service(db: Session = Depends(get_db)) -> PacienteService:
    """Dependency para PacienteService"""
    return PacienteService(
        paciente_repo=PacienteRepo(db),
        auditoria_repo=AuditoriaRepo(db)
    )


@router.get("", response_model=List[PacienteListItemDTO])
def listar_pacientes(
    buscar: Optional[str] = Query(None, description="Buscar por RUT o nombre"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),  # Cualquier autenticado
    service: PacienteService = Depends(get_paciente_service)
):
    """
    🔒 **Autenticado** - Listar pacientes con búsqueda.

    Todos los roles pueden ver la lista.
    """
    return service.listar_pacientes(buscar=buscar, skip=skip, limit=limit)


@router.get("/{paciente_id}", response_model=PacienteResponseDTO)
def obtener_paciente(
    paciente_id: str,
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),
    service: PacienteService = Depends(get_paciente_service)
):
    """
    🔒 **Autenticado** - Obtener detalle de paciente.

    Todos los roles pueden ver detalles.
    """
    try:
        paciente = service.obtener_por_id(UUID(paciente_id))
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return paciente
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=PacienteResponseDTO, status_code=status.HTTP_201_CREATED)
def crear_paciente(
    dto: PacienteCreateDTO,
    usuario_actual: UsuarioActual = Depends(obtener_usuario_actual),
    service: PacienteService = Depends(get_paciente_service)
):
    """
    🔒 **Admin + Profesional** - Crear nuevo paciente.

    - Admin: puede crear con todos los datos
    - Profesional: solo datos demográficos básicos (sin historial clínico)
    - Administrativo: sin acceso
    """
    # Validar que el usuario tenga permiso
    if not usuario_actual.es_admin() and not usuario_actual.es_profesional():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear pacientes"
        )

    # Si es profesional, validar que solo envíe datos demográficos
    if usuario_actual.es_profesional():
        if dto.historial_clinico or dto.alergias or dto.medicamentos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Los profesionales solo pueden crear pacientes con datos demográficos"
            )

    try:
        return service.crear_paciente(dto, creado_por_id=UUID(usuario_actual.user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{paciente_id}", response_model=PacienteResponseDTO)
def actualizar_paciente(
    paciente_id: str,
    dto: PacienteCreateDTO,
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),  # Solo admin
    service: PacienteService = Depends(get_paciente_service)
):
    """
    🔒 **Solo Admin** - Actualizar paciente.

    Solo administradores pueden editar pacientes.
    """
    try:
        return service.actualizar_paciente(
            paciente_id=UUID(paciente_id),
            dto=dto,
            actualizado_por_id=UUID(usuario_actual.user_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_paciente(
    paciente_id: str,
    usuario_actual: UsuarioActual = Depends(RequiereAdmin),  # Solo admin
    service: PacienteService = Depends(get_paciente_service)
):
    """
    🔒 **Solo Admin** - Eliminar paciente (soft delete).
    """
    try:
        service.eliminar_paciente(
            paciente_id=UUID(paciente_id),
            eliminado_por_id=UUID(usuario_actual.user_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 6.3 Configuración de Permisos Detallados

```python
# app/infraestructura/seguridad/permissions.py

from typing import Dict, Set, Callable
from app.infraestructura.seguridad.rbac import UsuarioActual
from fastapi import HTTPException, status


class Permiso:
    """Clase para definir permisos granulares"""

    MATRIZ_PERMISOS: Dict[str, Dict[str, Set[str]]] = {
        "admin": {
            "usuarios_sistema": {"crear", "listar", "aprobar", "editar", "eliminar"},
            "pacientes": {"crear", "listar", "ver", "editar", "eliminar"},
            "boxes": {"crear", "listar", "ver", "editar", "eliminar"},
            "prestaciones": {"crear", "listar", "ver", "editar", "eliminar"},
            "profesionales": {"crear", "listar", "ver", "editar", "eliminar"},
            "citas": {"crear", "listar", "ver", "editar", "eliminar"},
            "atenciones": {"registrar", "listar", "ver", "editar"},
            "reportes": {"ver_todos", "exportar"}
        },
        "profesional": {
            "pacientes": {"crear_demografico", "listar", "ver"},
            "boxes": {"listar", "ver"},
            "citas": {"listar_propias", "ver"},
            "atenciones": {"registrar_propias", "listar_propias", "ver_propias"},
            "reportes": {"ver_propios"}
        },
        "administrativo": {
            "pacientes": {"listar", "ver"},
            "boxes": {"listar", "ver"},
            "prestaciones": {"listar", "ver"},
            "profesionales": {"listar", "ver"},
            "citas": {"listar", "ver"},
            "atenciones": {"listar", "ver"},
            "reportes": {"ver_generales"}
        }
    }

    @classmethod
    def tiene_permiso(cls, usuario: UsuarioActual, recurso: str, accion: str) -> bool:
        """Verifica si el usuario tiene permiso para realizar una acción"""
        permisos_rol = cls.MATRIZ_PERMISOS.get(usuario.rol, {})
        permisos_recurso = permisos_rol.get(recurso, set())
        return accion in permisos_recurso

    @classmethod
    def requiere_permiso(cls, recurso: str, accion: str) -> Callable:
        """
        Decorator para requerir permiso específico.

        Uso:
            @router.get("/pacientes")
            @Permiso.requiere_permiso("pacientes", "listar")
            def listar_pacientes(usuario: UsuarioActual = Depends(...)):
                pass
        """
        def decorator(func):
            def wrapper(*args, usuario_actual: UsuarioActual, **kwargs):
                if not cls.tiene_permiso(usuario_actual, recurso, accion):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"No tienes permiso para {accion} en {recurso}"
                    )
                return func(*args, usuario_actual=usuario_actual, **kwargs)
            return wrapper
        return decorator


# Ejemplo de uso avanzado
class RequierePermisoResource:
    """Dependency para verificar permisos sobre recursos específicos"""

    def __init__(self, recurso: str, accion: str, verificar_propiedad: bool = False):
        self.recurso = recurso
        self.accion = accion
        self.verificar_propiedad = verificar_propiedad

    async def __call__(self, usuario: UsuarioActual):
        if not Permiso.tiene_permiso(usuario, self.recurso, self.accion):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para {self.accion} en {self.recurso}"
            )

        # Si es profesional y la acción es "propias", validar ownership en el handler
        if self.verificar_propiedad and usuario.es_profesional():
            # Esta validación se debe hacer en el handler
            pass

        return usuario
```

---

## [7] INTEGRACIÓN EN main.py

```python
# app/presentacion/api_rest/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.presentacion.api_rest.routers import (
    auth_router,
    usuarios_router,
    pacientes_router,
    boxes_router,
    citas_router,
    atenciones_router,
    reportes_router,
    perfil_router
)

app = FastAPI(
    title="API Agenda Clínica",
    description="Sistema de gestión de agenda clínica con RBAC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router.router)
app.include_router(usuarios_router.router)
app.include_router(pacientes_router.router)
app.include_router(boxes_router.router)
app.include_router(citas_router.router)
app.include_router(atenciones_router.router)
app.include_router(reportes_router.router)
app.include_router(perfil_router.router)


@app.get("/")
def root():
    return {
        "message": "API Agenda Clínica",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Endpoint de health check"""
    return {"status": "ok"}
```

---

✅ **Routers y permisos completados**
