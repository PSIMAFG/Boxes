"""
DTOs comunes para Profesional, Box, Prestacion, Alerta
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID


# ===== PROFESIONAL =====
class ProfesionalCreateDTO(BaseModel):
    """DTO para creación de profesional"""
    nombre: str = Field(..., min_length=3, max_length=255)
    profesion: str = Field(..., min_length=3, max_length=100)


class ProfesionalUpdateDTO(BaseModel):
    """DTO para actualización de profesional"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    profesion: Optional[str] = Field(None, min_length=3, max_length=100)
    activo: Optional[bool] = None


class ProfesionalResponseDTO(BaseModel):
    """DTO para respuesta de profesional"""
    id: UUID
    nombre: str
    profesion: str
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ===== BOX =====
class BoxCreateDTO(BaseModel):
    """DTO para creación de box"""
    nombre: str = Field(..., min_length=2, max_length=100)
    ubicacion: str = Field(..., max_length=255)


class BoxUpdateDTO(BaseModel):
    """DTO para actualización de box"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    ubicacion: Optional[str] = None
    activo: Optional[bool] = None


class BoxResponseDTO(BaseModel):
    """DTO para respuesta de box"""
    id: UUID
    nombre: str
    ubicacion: str
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ===== PRESTACION =====
class PrestacionCreateDTO(BaseModel):
    """DTO para creación de prestación"""
    nombre: str = Field(..., max_length=200)
    duracion_minutos: int = Field(..., gt=0, le=480)
    periodicidad_dias: int = Field(..., gt=0)
    tolerancia_dias: int = Field(..., ge=0)


class PrestacionUpdateDTO(BaseModel):
    """DTO para actualización de prestación"""
    nombre: Optional[str] = None
    duracion_minutos: Optional[int] = Field(None, gt=0, le=480)
    periodicidad_dias: Optional[int] = Field(None, gt=0)
    tolerancia_dias: Optional[int] = Field(None, ge=0)
    habilitada: Optional[bool] = None


class PrestacionResponseDTO(BaseModel):
    """DTO para respuesta de prestación"""
    id: UUID
    nombre: str
    duracion_minutos: int
    periodicidad_dias: int
    tolerancia_dias: int
    habilitada: bool
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


# ===== ALERTA =====
class AlertaResponseDTO(BaseModel):
    """DTO para respuesta de alerta"""
    id: UUID
    usuario_id: UUID
    prestacion_id: UUID
    nivel: Literal["info", "warn", "crit"]
    motivo: str
    fecha_objetivo: date
    resuelta: bool
    creado_en: datetime
    resuelta_en: Optional[datetime]

    class Config:
        from_attributes = True


# ===== BLOQUEO =====
class BloqueoCreateDTO(BaseModel):
    """DTO para creación de bloqueo"""
    scope: Literal["box", "profesional"]
    box_id: Optional[UUID] = None
    profesional_id: Optional[UUID] = None
    inicio: datetime
    fin: datetime
    motivo: str


class BloqueoResponseDTO(BaseModel):
    """DTO para respuesta de bloqueo"""
    id: UUID
    scope: str
    box_id: Optional[UUID]
    profesional_id: Optional[UUID]
    inicio: datetime
    fin: datetime
    motivo: str
    creado_en: datetime
    creado_por: UUID

    class Config:
        from_attributes = True


# ===== ANALITICA / KPIs =====
class KPIsResponseDTO(BaseModel):
    """DTO para respuesta de KPIs"""
    tasa_ocupacion_global: float
    tasa_no_show: float
    usuarios_bajo_control: int
    usuarios_fuera_control: int
    citas_dia_promedio: float
    citas_semana_promedio: float
    alertas_pendientes_total: int
    alertas_criticas: int
