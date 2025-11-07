"""
Router para endpoints de estadísticas de boxes.
Proporciona endpoints para visualización y simulación de uso.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from app.infraestructura.db.database import get_db
from app.aplicacion.servicios.box_estadisticas_servicio import BoxEstadisticasServicio
from app.presentacion.api_rest.dependencias import get_current_user
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/uso/por-hora")
def obtener_uso_por_hora(
    box_id: Optional[UUID] = Query(None, description="ID del box (opcional, todos si no se especifica)"),
    fecha: Optional[date] = Query(None, description="Fecha a analizar (default: hoy)"),
    hora_inicio: int = Query(8, ge=0, le=23, description="Hora de inicio (0-23)"),
    hora_fin: int = Query(20, ge=1, le=24, description="Hora de fin (1-24)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene estadísticas de uso de boxes por hora.

    **Parámetros:**
    - **box_id**: ID del box específico (opcional)
    - **fecha**: Fecha a analizar en formato YYYY-MM-DD (default: hoy)
    - **hora_inicio**: Hora de inicio del análisis (default: 8am)
    - **hora_fin**: Hora de fin del análisis (default: 8pm)

    **Retorna:**
    - Estadísticas de ocupación por hora con porcentajes de uso
    - Hora más ocupada y menos ocupada del día
    """
    try:
        servicio = BoxEstadisticasServicio(db)
        return servicio.calcular_uso_por_hora(box_id, fecha, hora_inicio, hora_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uso/por-dia")
def obtener_uso_por_dia(
    box_id: Optional[UUID] = Query(None, description="ID del box (opcional)"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio (default: hace 7 días)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin (default: hoy)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene estadísticas de uso de boxes por día.

    **Parámetros:**
    - **box_id**: ID del box específico (opcional)
    - **fecha_inicio**: Fecha de inicio del análisis (default: hace 7 días)
    - **fecha_fin**: Fecha de fin del análisis (default: hoy)

    **Retorna:**
    - Estadísticas de ocupación por día con porcentajes de uso
    - Día más ocupado y menos ocupado del período
    - Promedio de uso del período
    """
    try:
        servicio = BoxEstadisticasServicio(db)
        return servicio.calcular_uso_por_dia(box_id, fecha_inicio, fecha_fin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uso/por-semana")
def obtener_uso_por_semana(
    box_id: Optional[UUID] = Query(None, description="ID del box (opcional)"),
    semanas: int = Query(4, ge=1, le=52, description="Número de semanas a analizar"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene estadísticas de uso de boxes por semana.

    **Parámetros:**
    - **box_id**: ID del box específico (opcional)
    - **semanas**: Número de semanas hacia atrás a analizar (default: 4)

    **Retorna:**
    - Estadísticas de ocupación por semana con porcentajes de uso
    - Semana más ocupada y menos ocupada
    - Promedio de uso del período
    """
    try:
        servicio = BoxEstadisticasServicio(db)
        return servicio.calcular_uso_por_semana(box_id, semanas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uso/por-piso")
def obtener_uso_por_piso(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene estadísticas de uso agrupadas por piso.

    **Retorna:**
    - Listado de boxes por piso (Piso 1, Piso 2, Sin asignar)
    - Ocupación actual de cada piso
    - Estadísticas generales por piso
    """
    try:
        servicio = BoxEstadisticasServicio(db)
        return servicio.obtener_estadisticas_por_piso()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulacion/ocupacion-futura")
def simular_ocupacion_futura(
    dias_adelante: int = Query(7, ge=1, le=90, description="Días hacia adelante a simular"),
    box_id: Optional[UUID] = Query(None, description="ID del box (opcional)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Simula la ocupación futura de boxes basada en citas programadas.

    **Parámetros:**
    - **dias_adelante**: Días hacia adelante a proyectar (default: 7)
    - **box_id**: ID del box específico (opcional)

    **Retorna:**
    - Proyección de ocupación día por día
    - Citas programadas por día
    - Porcentaje de uso proyectado
    """
    try:
        servicio = BoxEstadisticasServicio(db)
        return servicio.simular_ocupacion_futura(dias_adelante, box_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
def obtener_dashboard_completo(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene un dashboard completo con todas las estadísticas principales.

    **Retorna:**
    - Uso actual por hora (hoy)
    - Uso de la última semana
    - Uso por piso
    - Proyección para los próximos 7 días
    """
    try:
        servicio = BoxEstadisticasServicio(db)

        return {
            "timestamp": datetime.now().isoformat(),
            "uso_hoy": servicio.calcular_uso_por_hora(fecha=date.today()),
            "uso_ultima_semana": servicio.calcular_uso_por_dia(
                fecha_inicio=date.today() - timedelta(days=7),
                fecha_fin=date.today()
            ),
            "uso_por_piso": servicio.obtener_estadisticas_por_piso(),
            "proyeccion_7_dias": servicio.simular_ocupacion_futura(dias_adelante=7)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import timedelta at the top
from datetime import timedelta
