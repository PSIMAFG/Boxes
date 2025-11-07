"""
Routers de la API REST.
"""
from . import (
    auth_router,
    usuarios_router,
    profesionales_router,
    boxes_router,
    prestaciones_router,
    citas_router,
    alertas_router,
    analitica_router,
)

__all__ = [
    "auth_router",
    "usuarios_router",
    "profesionales_router",
    "boxes_router",
    "prestaciones_router",
    "citas_router",
    "alertas_router",
    "analitica_router",
]
