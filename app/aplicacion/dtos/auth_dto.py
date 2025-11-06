"""
DTOs para Autenticación
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from uuid import UUID


class LoginRequestDTO(BaseModel):
    """DTO para login"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponseDTO(BaseModel):
    """DTO para respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    rol: str


class UsuarioSistemaCreateDTO(BaseModel):
    """DTO para creación de usuario del sistema"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    rol: Literal["admin", "profesional", "recepcion"]
    profesional_id: UUID | None = None


class UsuarioSistemaResponseDTO(BaseModel):
    """DTO para respuesta de usuario del sistema"""
    id: UUID
    email: str
    rol: str
    activo: bool
    profesional_id: UUID | None

    class Config:
        from_attributes = True


class CambiarPasswordDTO(BaseModel):
    """DTO para cambiar contraseña"""
    password_actual: str
    password_nuevo: str = Field(..., min_length=6)
