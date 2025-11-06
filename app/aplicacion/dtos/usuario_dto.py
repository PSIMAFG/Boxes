"""
DTOs para Usuario
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Literal
from uuid import UUID


class UsuarioCreateDTO(BaseModel):
    """DTO para creación de usuario"""
    rut: str = Field(..., description="RUT chileno en formato 12345678-5")
    nombre: str = Field(..., min_length=3, max_length=255)
    fecha_nacimiento: date
    nivel_apoyo: Optional[Literal[1, 2, 3]] = None


class UsuarioUpdateDTO(BaseModel):
    """DTO para actualización de usuario"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    fecha_nacimiento: Optional[date] = None
    nivel_apoyo: Optional[Literal[1, 2, 3]] = None
    activo: Optional[bool] = None


class UsuarioResponseDTO(BaseModel):
    """DTO para respuesta de usuario"""
    id: UUID
    rut: str
    nombre: str
    fecha_nacimiento: date
    nivel_apoyo: Optional[Literal[1, 2, 3]]
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    edad: int

    class Config:
        from_attributes = True
