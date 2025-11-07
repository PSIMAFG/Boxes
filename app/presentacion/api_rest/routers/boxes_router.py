"""
Router de boxes - CRUD completo con soporte para gestión de pisos y características.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.infraestructura.db.database import get_db
from app.infraestructura.repos.box_repo import BoxRepo
from app.dominio.entidades import Box
from app.infraestructura.seguridad.rbac import RequiereRecepcion
from app.presentacion.api_rest.dependencias import get_current_user


router = APIRouter()


class BoxCreate(BaseModel):
    """Esquema para creación de box"""
    nombre: str = Field(..., min_length=2, max_length=100)
    ubicacion: str = Field(..., min_length=3, max_length=255)
    piso: Optional[int] = Field(None, ge=1, le=2, description="Piso 1 o 2")
    capacidad: int = Field(1, ge=1, description="Capacidad del box")
    equipamiento: Optional[str] = Field(None, description="Equipamiento disponible (JSON)")
    caracteristicas: Optional[str] = Field(None, description="Características especiales (JSON)")
    activo: bool = True


class BoxUpdate(BaseModel):
    """Esquema para actualización de box"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    ubicacion: Optional[str] = Field(None, min_length=3, max_length=255)
    piso: Optional[int] = Field(None, ge=1, le=2, description="Piso 1 o 2")
    capacidad: Optional[int] = Field(None, ge=1, description="Capacidad del box")
    equipamiento: Optional[str] = Field(None, description="Equipamiento disponible (JSON)")
    caracteristicas: Optional[str] = Field(None, description="Características especiales (JSON)")
    activo: Optional[bool] = None


class BoxResponse(BaseModel):
    """Esquema de respuesta para box"""
    id: UUID
    nombre: str
    ubicacion: str
    piso: Optional[int]
    capacidad: int
    equipamiento: Optional[str]
    caracteristicas: Optional[str]
    activo: bool
    creado_en: str
    actualizado_en: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[BoxResponse])
def listar_boxes(
    piso: Optional[int] = Query(None, ge=1, le=2, description="Filtrar por piso"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    """
    Lista todos los boxes.

    **Parámetros opcionales:**
    - **piso**: Filtrar por piso (1 o 2)
    - **activo**: Filtrar por estado activo (true/false)
    """
    try:
        repo = BoxRepo(db)

        if activo is False:
            boxes = repo.listar_todos()
        else:
            boxes = repo.listar_activos()

        # Filtrar por piso si se especifica
        if piso is not None:
            boxes = [b for b in boxes if b.piso == piso]

        return [
            BoxResponse(
                id=box.id,
                nombre=box.nombre,
                ubicacion=box.ubicacion,
                piso=box.piso,
                capacidad=box.capacidad,
                equipamiento=box.equipamiento,
                caracteristicas=box.caracteristicas,
                activo=box.activo,
                creado_en=box.creado_en.isoformat(),
                actualizado_en=box.actualizado_en.isoformat()
            )
            for box in boxes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{box_id}", response_model=BoxResponse)
def obtener_box(
    box_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)
):
    """Obtiene un box por ID"""
    try:
        repo = BoxRepo(db)
        box = repo.obtener_por_id(box_id)

        if not box:
            raise HTTPException(status_code=404, detail="Box no encontrado")

        return BoxResponse(
            id=box.id,
            nombre=box.nombre,
            ubicacion=box.ubicacion,
            piso=box.piso,
            capacidad=box.capacidad,
            equipamiento=box.equipamiento,
            caracteristicas=box.caracteristicas,
            activo=box.activo,
            creado_en=box.creado_en.isoformat(),
            actualizado_en=box.actualizado_en.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BoxResponse, status_code=201)
def crear_box(
    box_data: BoxCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(RequiereRecepcion)
):
    """
    Crea un nuevo box.

    **Requiere rol:** Recepción o superior
    """
    try:
        repo = BoxRepo(db)

        box = Box(
            nombre=box_data.nombre,
            ubicacion=box_data.ubicacion,
            piso=box_data.piso,
            capacidad=box_data.capacidad,
            equipamiento=box_data.equipamiento,
            caracteristicas=box_data.caracteristicas,
            activo=box_data.activo
        )

        box_creado = repo.crear(box)

        return BoxResponse(
            id=box_creado.id,
            nombre=box_creado.nombre,
            ubicacion=box_creado.ubicacion,
            piso=box_creado.piso,
            capacidad=box_creado.capacidad,
            equipamiento=box_creado.equipamiento,
            caracteristicas=box_creado.caracteristicas,
            activo=box_creado.activo,
            creado_en=box_creado.creado_en.isoformat(),
            actualizado_en=box_creado.actualizado_en.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{box_id}", response_model=BoxResponse)
def actualizar_box(
    box_id: UUID,
    box_data: BoxUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(RequiereRecepcion)
):
    """
    Actualiza un box existente.

    **Requiere rol:** Recepción o superior

    Permite modificar características del box en el tiempo.
    """
    try:
        repo = BoxRepo(db)
        box = repo.obtener_por_id(box_id)

        if not box:
            raise HTTPException(status_code=404, detail="Box no encontrado")

        # Actualizar solo los campos proporcionados
        if box_data.nombre is not None:
            box.nombre = box_data.nombre
        if box_data.ubicacion is not None:
            box.ubicacion = box_data.ubicacion
        if box_data.piso is not None:
            box.piso = box_data.piso
        if box_data.capacidad is not None:
            box.capacidad = box_data.capacidad
        if box_data.equipamiento is not None:
            box.equipamiento = box_data.equipamiento
        if box_data.caracteristicas is not None:
            box.caracteristicas = box_data.caracteristicas
        if box_data.activo is not None:
            box.activo = box_data.activo

        box_actualizado = repo.actualizar(box)

        return BoxResponse(
            id=box_actualizado.id,
            nombre=box_actualizado.nombre,
            ubicacion=box_actualizado.ubicacion,
            piso=box_actualizado.piso,
            capacidad=box_actualizado.capacidad,
            equipamiento=box_actualizado.equipamiento,
            caracteristicas=box_actualizado.caracteristicas,
            activo=box_actualizado.activo,
            creado_en=box_actualizado.creado_en.isoformat(),
            actualizado_en=box_actualizado.actualizado_en.isoformat()
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{box_id}", status_code=204)
def eliminar_box(
    box_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual = Depends(RequiereRecepcion)
):
    """
    Elimina (desactiva) un box.

    **Requiere rol:** Recepción o superior

    Nota: Esta operación desactiva el box en lugar de eliminarlo físicamente.
    """
    try:
        repo = BoxRepo(db)
        box = repo.obtener_por_id(box_id)

        if not box:
            raise HTTPException(status_code=404, detail="Box no encontrado")

        repo.eliminar(box_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
