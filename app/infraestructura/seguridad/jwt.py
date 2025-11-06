"""
Funciones para manejo de JWT tokens.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config.settings import settings


def crear_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token.

    Args:
        data: Payload del token (user_id, email, rol, etc.)
        expires_delta: Tiempo de expiración custom (o usa default de settings)

    Returns:
        Token JWT como string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verificar_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un JWT token.

    Args:
        token: Token JWT a verificar

    Returns:
        Payload del token si es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def extraer_user_id(token: str) -> Optional[str]:
    """
    Extrae el user_id de un token JWT.

    Args:
        token: Token JWT

    Returns:
        user_id como string, o None si el token es inválido
    """
    payload = verificar_token(token)
    if payload:
        return payload.get("user_id")
    return None


def extraer_email(token: str) -> Optional[str]:
    """
    Extrae el email de un token JWT.

    Args:
        token: Token JWT

    Returns:
        email como string, o None si el token es inválido
    """
    payload = verificar_token(token)
    if payload:
        return payload.get("email")
    return None


def extraer_rol(token: str) -> Optional[str]:
    """
    Extrae el rol de un token JWT.

    Args:
        token: Token JWT

    Returns:
        rol como string, o None si el token es inválido
    """
    payload = verificar_token(token)
    if payload:
        return payload.get("rol")
    return None
