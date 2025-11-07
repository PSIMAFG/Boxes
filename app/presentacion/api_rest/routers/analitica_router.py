"""
Router para análisis y estadísticas de uso de boxes.
"""
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.infraestructura.db.database import get_db
from app.infraestructura.seguridad.auth import get_current_user
from app.dominio.entidades import UsuarioSistema
from app.aplicacion.servicios.analitica_service import AnaliticaBoxService
from app.aplicacion.dtos.analitica_dto import (
    UsoHorarioDTO,
    UsoDiarioDTO,
    UsoSemanalDTO,
    EstadisticaBoxDTO,
    ComparativaBoxesDTO,
    HistorialBoxDTO,
    ActualizarBoxCaracteristicasDTO
)

router = APIRouter()


@router.get("/boxes/{box_id}/uso-horario", response_model=List[UsoHorarioDTO])
def obtener_uso_horario(
    box_id: UUID,
    fecha: date = Query(..., description="Fecha del día a analizar (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Obtiene el uso de un box hora por hora en un día específico.

    Muestra cuántos minutos estuvo ocupado el box en cada hora del día (0-23).
    """
    service = AnaliticaBoxService(db)

    try:
        return service.obtener_uso_horario(box_id, fecha)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular uso horario: {str(e)}"
        )


@router.get("/boxes/{box_id}/uso-diario", response_model=UsoDiarioDTO)
def obtener_uso_diario(
    box_id: UUID,
    fecha: date = Query(..., description="Fecha del día a analizar (YYYY-MM-DD)"),
    incluir_horas: bool = Query(False, description="Incluir detalle hora por hora"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Obtiene el uso total de un box en un día específico.

    Incluye:
    - Minutos totales ocupados
    - Porcentaje de uso
    - Número de citas
    - Opcionalmente: detalle hora por hora
    """
    service = AnaliticaBoxService(db)

    try:
        return service.obtener_uso_diario(box_id, fecha, incluir_horas)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular uso diario: {str(e)}"
        )


@router.get("/boxes/{box_id}/uso-semanal", response_model=UsoSemanalDTO)
def obtener_uso_semanal(
    box_id: UUID,
    fecha: date = Query(..., description="Cualquier fecha dentro de la semana a analizar"),
    incluir_dias: bool = Query(False, description="Incluir detalle día por día"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Obtiene el uso de un box en una semana completa (lunes a domingo).

    Incluye:
    - Minutos totales ocupados en la semana
    - Porcentaje de uso promedio
    - Número total de citas
    - Opcionalmente: detalle día por día
    """
    service = AnaliticaBoxService(db)

    try:
        return service.obtener_uso_semanal(box_id, fecha, incluir_dias)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular uso semanal: {str(e)}"
        )


@router.get("/boxes/{box_id}/estadisticas", response_model=EstadisticaBoxDTO)
def obtener_estadisticas_box(
    box_id: UUID,
    fecha_inicio: datetime = Query(..., description="Inicio del período a analizar"),
    fecha_fin: datetime = Query(..., description="Fin del período a analizar"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Obtiene estadísticas completas de un box en un período personalizado.

    Muestra:
    - Total de minutos ocupados y disponibles
    - Porcentaje de uso promedio
    - Total de citas
    - Información del box (piso, capacidad)
    """
    service = AnaliticaBoxService(db)

    try:
        return service.obtener_estadisticas_box(box_id, fecha_inicio, fecha_fin)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular estadísticas: {str(e)}"
        )


@router.get("/boxes/comparativa", response_model=ComparativaBoxesDTO)
def obtener_comparativa_boxes(
    fecha_inicio: datetime = Query(..., description="Inicio del período"),
    fecha_fin: datetime = Query(..., description="Fin del período"),
    box_ids: Optional[str] = Query(None, description="IDs de boxes separados por comas"),
    piso: Optional[int] = Query(None, ge=1, le=2, description="Filtrar por piso (1 o 2)"),
    incluir_inactivos: bool = Query(False, description="Incluir boxes inactivos"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Compara el uso de múltiples boxes en un período.

    Muestra:
    - Estadísticas individuales de cada box
    - Porcentaje de uso promedio por piso
    - Box con mayor y menor uso
    - Comparativa visual de ocupación
    """
    service = AnaliticaBoxService(db)

    # Parsear box_ids si se proporcionaron
    box_ids_list = None
    if box_ids:
        try:
            box_ids_list = [UUID(id.strip()) for id in box_ids.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IDs de boxes inválidos"
            )

    try:
        return service.obtener_comparativa_boxes(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            box_ids=box_ids_list,
            piso=piso,
            incluir_inactivos=incluir_inactivos
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar comparativa: {str(e)}"
        )


@router.get("/boxes/{box_id}/historial", response_model=List[HistorialBoxDTO])
def obtener_historial_box(
    box_id: UUID,
    fecha_inicio: Optional[datetime] = Query(None, description="Filtrar desde esta fecha"),
    fecha_fin: Optional[datetime] = Query(None, description="Filtrar hasta esta fecha"),
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Obtiene el historial de cambios de un box.

    Muestra todos los cambios realizados en características del box:
    - Cambios de piso
    - Cambios de capacidad
    - Cambios de equipamiento
    - Cambios de ubicación
    - Activación/desactivación
    """
    service = AnaliticaBoxService(db)

    try:
        return service.obtener_historial_box(box_id, fecha_inicio, fecha_fin)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.patch("/boxes/{box_id}/caracteristicas")
def actualizar_caracteristicas_box(
    box_id: UUID,
    datos: ActualizarBoxCaracteristicasDTO,
    db: Session = Depends(get_db),
    current_user: UsuarioSistema = Depends(get_current_user)
):
    """
    Actualiza las características de un box y registra el cambio en el historial.

    Solo usuarios admin pueden realizar esta operación.

    Los cambios quedan registrados en el historial para análisis futuro.
    """
    # Verificar permisos
    if not current_user.es_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden modificar características de boxes"
        )

    from app.infraestructura.repos.box_repo import BoxRepo

    try:
        # Obtener box actual
        box_repo = BoxRepo(db)
        box = box_repo.obtener_por_id(box_id)

        if not box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Box con ID {box_id} no encontrado"
            )

        service = AnaliticaBoxService(db)

        # Registrar cambios en historial
        cambios_realizados = []

        if datos.piso is not None and datos.piso != box.piso:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="piso",
                valor_anterior=str(box.piso),
                valor_nuevo=str(datos.piso),
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.piso = datos.piso
            cambios_realizados.append("piso")

        if datos.capacidad is not None and datos.capacidad != box.capacidad:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="capacidad",
                valor_anterior=str(box.capacidad),
                valor_nuevo=str(datos.capacidad),
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.capacidad = datos.capacidad
            cambios_realizados.append("capacidad")

        if datos.equipamiento is not None and datos.equipamiento != box.equipamiento:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="equipamiento",
                valor_anterior=box.equipamiento or "",
                valor_nuevo=datos.equipamiento,
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.equipamiento = datos.equipamiento
            cambios_realizados.append("equipamiento")

        if datos.metros_cuadrados is not None and datos.metros_cuadrados != box.metros_cuadrados:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="metros_cuadrados",
                valor_anterior=str(box.metros_cuadrados) if box.metros_cuadrados else "",
                valor_nuevo=str(datos.metros_cuadrados),
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.metros_cuadrados = datos.metros_cuadrados
            cambios_realizados.append("metros_cuadrados")

        if datos.ubicacion is not None and datos.ubicacion != box.ubicacion:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="ubicacion",
                valor_anterior=box.ubicacion,
                valor_nuevo=datos.ubicacion,
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.ubicacion = datos.ubicacion
            cambios_realizados.append("ubicacion")

        if datos.activo is not None and datos.activo != box.activo:
            service.registrar_cambio_box(
                box_id=box_id,
                campo="activo",
                valor_anterior=str(box.activo),
                valor_nuevo=str(datos.activo),
                usuario_id=current_user.id,
                motivo=datos.motivo_cambio
            )
            box.activo = datos.activo
            cambios_realizados.append("activo")

        # Actualizar box
        if cambios_realizados:
            box_actualizado = box_repo.actualizar(box)
            return {
                "mensaje": "Box actualizado exitosamente",
                "cambios_realizados": cambios_realizados,
                "box": {
                    "id": str(box_actualizado.id),
                    "nombre": box_actualizado.nombre,
                    "piso": box_actualizado.piso,
                    "capacidad": box_actualizado.capacidad,
                    "equipamiento": box_actualizado.equipamiento,
                    "metros_cuadrados": box_actualizado.metros_cuadrados,
                    "ubicacion": box_actualizado.ubicacion,
                    "activo": box_actualizado.activo
                }
            }
        else:
            return {
                "mensaje": "No se realizaron cambios",
                "cambios_realizados": []
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar box: {str(e)}"
        )
