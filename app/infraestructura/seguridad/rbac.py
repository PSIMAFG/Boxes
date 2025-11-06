"""
Control de acceso basado en roles (RBAC).
"""
from typing import List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infraestructura.seguridad.jwt import verificar_token

security = HTTPBearer()


class UsuarioActual:
    """Información del usuario autenticado actual"""

    def __init__(self, user_id: str, email: str, rol: str):
        self.user_id = user_id
        self.email = email
        self.rol = rol

    def es_admin(self) -> bool:
        return self.rol == "admin"

    def es_profesional(self) -> bool:
        return self.rol == "profesional"

    def es_recepcion(self) -> bool:
        return self.rol == "recepcion"


async def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UsuarioActual:
    """
    Dependency para obtener usuario actual desde JWT.
    Lanza 401 si token inválido.
    """
    token = credentials.credentials
    payload = verificar_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    email = payload.get("email")
    rol = payload.get("rol")

    if not user_id or not email or not rol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UsuarioActual(user_id=user_id, email=email, rol=rol)


class RequiereRoles:
    """
    Dependency para requerir roles específicos.

    Usage:
        @app.get("/admin-only")
        def admin_endpoint(usuario: UsuarioActual = Depends(RequiereRoles(["admin"]))):
            pass
    """

    def __init__(self, roles_permitidos: List[str]):
        self.roles_permitidos = roles_permitidos

    async def __call__(
        self,
        usuario: UsuarioActual = Depends(obtener_usuario_actual)
    ) -> UsuarioActual:
        if usuario.rol not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {', '.join(self.roles_permitidos)}"
            )
        return usuario


# Shortcuts para roles comunes
RequiereAdmin = RequiereRoles(["admin"])
RequiereProfesional = RequiereRoles(["profesional"])
RequiereRecepcion = RequiereRoles(["recepcion", "admin"])
RequiereAnyAuth = RequiereRoles(["admin", "profesional", "recepcion"])
