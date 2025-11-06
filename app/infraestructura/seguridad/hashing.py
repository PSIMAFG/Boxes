"""
Funciones para hashing y verificación de contraseñas usando bcrypt.
"""
from passlib.context import CryptContext
from app.config.settings import settings


# Contexto de hashing con bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def hash_password(password: str) -> str:
    """
    Genera hash de una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """
    Verifica si una contraseña plana coincide con un hash.

    Args:
        password_plano: Contraseña en texto plano
        password_hash: Hash almacenado

    Returns:
        True si coincide, False si no
    """
    return pwd_context.verify(password_plano, password_hash)


def necesita_actualizacion(password_hash: str) -> bool:
    """
    Verifica si un hash necesita actualizarse (algoritmo obsoleto o rounds bajos).

    Args:
        password_hash: Hash a verificar

    Returns:
        True si necesita actualización
    """
    return pwd_context.needs_update(password_hash)
