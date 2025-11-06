"""Router de profesionales - CRUD básico"""
from fastapi import APIRouter, Depends
from app.infraestructura.seguridad.rbac import RequiereRecepcion
router = APIRouter()

@router.get("")
def listar(usuario_actual = Depends(RequiereRecepcion)):
    return []

@router.get("/{id}")
def obtener(id: str, usuario_actual = Depends(RequiereRecepcion)):
    return {}

@router.post("")
def crear(usuario_actual = Depends(RequiereRecepcion)):
    return {}
