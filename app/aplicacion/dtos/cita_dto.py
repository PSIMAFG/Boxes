"""
DTOs para Cita
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID


class CitaCreateDTO(BaseModel):
    """DTO para creación de cita"""
    usuario_id: UUID
    profesional_id: UUID
    prestacion_id: UUID
    box_id: UUID
    inicio: datetime
    fin: datetime


class CitaUpdateDTO(BaseModel):
    """DTO para actualización de cita"""
    usuario_id: Optional[UUID] = None
    profesional_id: Optional[UUID] = None
    prestacion_id: Optional[UUID] = None
    box_id: Optional[UUID] = None
    inicio: Optional[datetime] = None
    fin: Optional[datetime] = None
    estado: Optional[Literal["programada", "confirmada", "cumplida", "no_asistio", "cancelada"]] = None


class CitaResponseDTO(BaseModel):
    """DTO para respuesta de cita"""
    id: UUID
    usuario_id: UUID
    profesional_id: UUID
    prestacion_id: UUID
    box_id: UUID
    inicio: datetime
    fin: datetime
    estado: str
    duracion_minutos: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class SugerirSlotsRequestDTO(BaseModel):
    """DTO para solicitar sugerencia de slots"""
    usuario_id: UUID
    profesional_id: UUID
    prestacion_id: UUID
    fecha_desde: datetime
    fecha_hasta: datetime
    incluir_ml_scoring: bool = False


class SlotSugeridoDTO(BaseModel):
    """DTO para un slot sugerido"""
    inicio: datetime
    fin: datetime
    box_id: UUID
    box_nombre: str
    score: Optional[float] = None  # Score ML opcional
    razones: list[str] = []  # Razones de la sugerencia


class SesionRegistroCreateDTO(BaseModel):
    """DTO para crear registro de sesión"""
    cita_id: UUID
    cumplida: bool
    valoracion: Optional[Literal["positivo", "neutro", "negativo"]] = None
    notas: Optional[str] = None


class SesionRegistroResponseDTO(BaseModel):
    """DTO para respuesta de registro de sesión"""
    id: UUID
    cita_id: UUID
    cumplida: bool
    valoracion: Optional[str]
    notas: Optional[str]
    creado_por: UUID
    creado_en: datetime

    class Config:
        from_attributes = True
