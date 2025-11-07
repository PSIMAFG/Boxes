"""
DTOs para análisis y estadísticas de uso de boxes.
"""
from datetime import datetime, date, time
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class UsoHorarioDTO(BaseModel):
    """Uso de box en una hora específica"""
    hora: int = Field(..., ge=0, le=23, description="Hora del día (0-23)")
    minutos_ocupados: int = Field(..., ge=0, description="Minutos ocupados en esa hora")
    minutos_disponibles: int = Field(..., ge=0, description="Minutos disponibles en esa hora")
    porcentaje_uso: float = Field(..., ge=0, le=100, description="Porcentaje de uso")
    numero_citas: int = Field(..., ge=0, description="Número de citas en esa hora")

    class Config:
        json_schema_extra = {
            "example": {
                "hora": 10,
                "minutos_ocupados": 45,
                "minutos_disponibles": 60,
                "porcentaje_uso": 75.0,
                "numero_citas": 1
            }
        }


class UsoDiarioDTO(BaseModel):
    """Uso de box en un día específico"""
    fecha: date = Field(..., description="Fecha del día")
    dia_semana: str = Field(..., description="Nombre del día de la semana")
    minutos_ocupados: int = Field(..., ge=0, description="Minutos totales ocupados")
    minutos_disponibles: int = Field(..., ge=0, description="Minutos totales disponibles")
    porcentaje_uso: float = Field(..., ge=0, le=100, description="Porcentaje de uso del día")
    numero_citas: int = Field(..., ge=0, description="Número de citas del día")
    uso_por_hora: List[UsoHorarioDTO] = Field(default_factory=list, description="Detalle hora por hora")

    class Config:
        json_schema_extra = {
            "example": {
                "fecha": "2025-01-15",
                "dia_semana": "Miércoles",
                "minutos_ocupados": 360,
                "minutos_disponibles": 540,
                "porcentaje_uso": 66.67,
                "numero_citas": 8,
                "uso_por_hora": []
            }
        }


class UsoSemanalDTO(BaseModel):
    """Uso de box en una semana específica"""
    semana: int = Field(..., ge=1, le=53, description="Número de semana del año")
    año: int = Field(..., description="Año")
    fecha_inicio: date = Field(..., description="Primer día de la semana")
    fecha_fin: date = Field(..., description="Último día de la semana")
    minutos_ocupados: int = Field(..., ge=0, description="Minutos totales ocupados en la semana")
    minutos_disponibles: int = Field(..., ge=0, description="Minutos totales disponibles en la semana")
    porcentaje_uso: float = Field(..., ge=0, le=100, description="Porcentaje de uso promedio")
    numero_citas: int = Field(..., ge=0, description="Número total de citas")
    uso_por_dia: List[UsoDiarioDTO] = Field(default_factory=list, description="Detalle día por día")

    class Config:
        json_schema_extra = {
            "example": {
                "semana": 3,
                "año": 2025,
                "fecha_inicio": "2025-01-13",
                "fecha_fin": "2025-01-19",
                "minutos_ocupados": 1800,
                "minutos_disponibles": 2700,
                "porcentaje_uso": 66.67,
                "numero_citas": 40,
                "uso_por_dia": []
            }
        }


class EstadisticaBoxDTO(BaseModel):
    """Estadísticas completas de uso de un box"""
    box_id: UUID = Field(..., description="ID del box")
    box_nombre: str = Field(..., description="Nombre del box")
    piso: int = Field(..., description="Piso donde está ubicado")
    capacidad: int = Field(..., description="Capacidad del box")
    periodo_inicio: datetime = Field(..., description="Inicio del período analizado")
    periodo_fin: datetime = Field(..., description="Fin del período analizado")

    # Estadísticas generales
    total_minutos_ocupados: int = Field(..., ge=0, description="Total de minutos ocupados")
    total_minutos_disponibles: int = Field(..., ge=0, description="Total de minutos disponibles")
    porcentaje_uso_promedio: float = Field(..., ge=0, le=100, description="Porcentaje de uso promedio")
    total_citas: int = Field(..., ge=0, description="Total de citas en el período")

    # Uso por piso
    uso_piso: Optional[float] = Field(None, description="Porcentaje de uso comparado con otros boxes del mismo piso")

    class Config:
        json_schema_extra = {
            "example": {
                "box_id": "123e4567-e89b-12d3-a456-426614174000",
                "box_nombre": "Box 1",
                "piso": 1,
                "capacidad": 1,
                "periodo_inicio": "2025-01-01T00:00:00",
                "periodo_fin": "2025-01-31T23:59:59",
                "total_minutos_ocupados": 7200,
                "total_minutos_disponibles": 10800,
                "porcentaje_uso_promedio": 66.67,
                "total_citas": 160,
                "uso_piso": 70.5
            }
        }


class ComparativaBoxesDTO(BaseModel):
    """Comparativa de uso entre múltiples boxes"""
    periodo_inicio: datetime = Field(..., description="Inicio del período")
    periodo_fin: datetime = Field(..., description="Fin del período")
    estadisticas_boxes: List[EstadisticaBoxDTO] = Field(..., description="Estadísticas por box")

    # Estadísticas por piso
    porcentaje_uso_piso_1: float = Field(..., ge=0, le=100, description="Uso promedio del piso 1")
    porcentaje_uso_piso_2: float = Field(..., ge=0, le=100, description="Uso promedio del piso 2")

    # Box con mayor y menor uso
    box_mayor_uso: Optional[EstadisticaBoxDTO] = Field(None, description="Box con mayor uso")
    box_menor_uso: Optional[EstadisticaBoxDTO] = Field(None, description="Box con menor uso")

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_inicio": "2025-01-01T00:00:00",
                "periodo_fin": "2025-01-31T23:59:59",
                "estadisticas_boxes": [],
                "porcentaje_uso_piso_1": 65.3,
                "porcentaje_uso_piso_2": 58.7,
                "box_mayor_uso": None,
                "box_menor_uso": None
            }
        }


class HistorialBoxDTO(BaseModel):
    """DTO para historial de cambios de un box"""
    id: UUID
    box_id: UUID
    campo_modificado: str
    valor_anterior: Optional[str]
    valor_nuevo: str
    motivo: Optional[str]
    modificado_por: UUID
    timestamp: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "box_id": "123e4567-e89b-12d3-a456-426614174001",
                "campo_modificado": "piso",
                "valor_anterior": "1",
                "valor_nuevo": "2",
                "motivo": "Reasignación por obras en piso 1",
                "modificado_por": "123e4567-e89b-12d3-a456-426614174002",
                "timestamp": "2025-01-15T10:30:00"
            }
        }


class ActualizarBoxCaracteristicasDTO(BaseModel):
    """DTO para actualizar características de un box"""
    piso: Optional[Literal[1, 2]] = Field(None, description="Piso del box")
    capacidad: Optional[int] = Field(None, ge=1, description="Capacidad del box")
    equipamiento: Optional[str] = Field(None, description="Equipamiento disponible")
    metros_cuadrados: Optional[float] = Field(None, gt=0, description="Metros cuadrados")
    ubicacion: Optional[str] = Field(None, description="Ubicación/dirección")
    activo: Optional[bool] = Field(None, description="Si el box está activo")
    motivo_cambio: Optional[str] = Field(None, description="Motivo del cambio")

    class Config:
        json_schema_extra = {
            "example": {
                "piso": 2,
                "capacidad": 2,
                "equipamiento": "Camilla eléctrica, ultrasonido",
                "metros_cuadrados": 15.5,
                "ubicacion": "Piso 2, Ala Norte",
                "activo": True,
                "motivo_cambio": "Ampliación de instalaciones"
            }
        }


class FiltroEstadisticasDTO(BaseModel):
    """Filtros para consultar estadísticas de uso"""
    fecha_inicio: datetime = Field(..., description="Fecha inicio del período")
    fecha_fin: datetime = Field(..., description="Fecha fin del período")
    box_ids: Optional[List[UUID]] = Field(None, description="IDs de boxes específicos a analizar")
    piso: Optional[Literal[1, 2]] = Field(None, description="Filtrar por piso")
    granularidad: Literal["hora", "dia", "semana"] = Field("dia", description="Nivel de detalle")
    incluir_inactivos: bool = Field(False, description="Incluir boxes inactivos")

    class Config:
        json_schema_extra = {
            "example": {
                "fecha_inicio": "2025-01-01T00:00:00",
                "fecha_fin": "2025-01-31T23:59:59",
                "box_ids": None,
                "piso": 1,
                "granularidad": "dia",
                "incluir_inactivos": False
            }
        }
