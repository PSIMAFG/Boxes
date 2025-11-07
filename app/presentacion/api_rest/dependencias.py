"""
Dependencias comunes para los endpoints de la API REST.

Este módulo centraliza las dependencias de FastAPI más utilizadas,
proporcionando una capa de abstracción clara para autenticación,
autorización y acceso a la base de datos.
"""
from app.infraestructura.seguridad.rbac import obtener_usuario_actual, UsuarioActual
from app.infraestructura.db.database import get_db

# Alias para compatibilidad con routers existentes
# Usa obtener_usuario_actual de RBAC que valida el JWT y retorna UsuarioActual
get_current_user = obtener_usuario_actual

__all__ = ['get_current_user', 'get_db', 'UsuarioActual']
