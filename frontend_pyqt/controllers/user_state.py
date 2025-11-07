"""
Gestión del estado de la sesión del usuario
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet

from resources.constants import SESSION_FILE, ENCRYPTION_KEY, Roles


class UserState:
    """Clase singleton para gestionar el estado de sesión del usuario"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserState, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._user_id: Optional[int] = None
            self._username: Optional[str] = None
            self._email: Optional[str] = None
            self._nombre_completo: Optional[str] = None
            self._role: Optional[str] = None
            self._access_token: Optional[str] = None
            self._refresh_token: Optional[str] = None
            self._token_expires_at: Optional[datetime] = None
            self._is_authenticated: bool = False
            self._cipher = self._get_cipher()
            UserState._initialized = True

    def _get_cipher(self) -> Optional[Fernet]:
        """Obtiene el cifrador Fernet para encriptar/desencriptar sesión"""
        try:
            if ENCRYPTION_KEY:
                return Fernet(ENCRYPTION_KEY.encode())
            else:
                # Si no hay key, generar una temporal (NO recomendado para producción)
                key = Fernet.generate_key()
                return Fernet(key)
        except Exception:
            return None

    def set_session(
        self,
        user_id: int,
        username: str,
        email: str,
        nombre_completo: str,
        role: str,
        access_token: str,
        refresh_token: str,
        expires_in: int = 900  # 15 minutos por defecto
    ):
        """
        Establece la sesión del usuario

        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            email: Email del usuario
            nombre_completo: Nombre completo
            role: Rol del usuario
            access_token: Token de acceso JWT
            refresh_token: Token de refresco
            expires_in: Tiempo de expiración en segundos
        """
        self._user_id = user_id
        self._username = username
        self._email = email
        self._nombre_completo = nombre_completo
        self._role = role
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        self._is_authenticated = True

    def update_tokens(self, access_token: str, expires_in: int = 900):
        """
        Actualiza los tokens de acceso

        Args:
            access_token: Nuevo token de acceso
            expires_in: Tiempo de expiración en segundos
        """
        self._access_token = access_token
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

    def clear_session(self):
        """Limpia la sesión del usuario"""
        self._user_id = None
        self._username = None
        self._email = None
        self._nombre_completo = None
        self._role = None
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None
        self._is_authenticated = False

    def is_authenticated(self) -> bool:
        """Verifica si el usuario está autenticado"""
        return self._is_authenticated and self._access_token is not None

    def is_token_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        if not self._token_expires_at:
            return True
        # Considera expirado si quedan menos de 60 segundos
        return datetime.now() >= (self._token_expires_at - timedelta(seconds=60))

    def needs_refresh(self) -> bool:
        """Verifica si se necesita refrescar el token"""
        return self.is_authenticated() and self.is_token_expired()

    # Getters
    @property
    def user_id(self) -> Optional[int]:
        return self._user_id

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def email(self) -> Optional[str]:
        return self._email

    @property
    def nombre_completo(self) -> Optional[str]:
        return self._nombre_completo

    @property
    def role(self) -> Optional[str]:
        return self._role

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    # Métodos de verificación de rol
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self._role == Roles.ADMIN

    def is_profesional(self) -> bool:
        """Verifica si el usuario es profesional"""
        return self._role == Roles.PROFESIONAL

    def is_administrativo(self) -> bool:
        """Verifica si el usuario es administrativo"""
        return self._role == Roles.ADMINISTRATIVO

    def has_role(self, role: str) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return self._role == role

    # Persistencia
    def save_to_file(self, remember_me: bool = False):
        """
        Guarda la sesión en archivo cifrado

        Args:
            remember_me: Si True, guarda también el refresh token
        """
        if not self.is_authenticated():
            return

        data = {
            "user_id": self._user_id,
            "username": self._username,
            "email": self._email,
            "nombre_completo": self._nombre_completo,
            "role": self._role,
            "access_token": self._access_token,
            "token_expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
        }

        if remember_me and self._refresh_token:
            data["refresh_token"] = self._refresh_token

        try:
            json_data = json.dumps(data)

            if self._cipher:
                # Cifrar datos
                encrypted_data = self._cipher.encrypt(json_data.encode())
                SESSION_FILE.write_bytes(encrypted_data)
            else:
                # Fallback sin cifrado (NO recomendado)
                SESSION_FILE.write_text(json_data)
        except Exception as e:
            print(f"Error al guardar sesión: {e}")

    def load_from_file(self) -> bool:
        """
        Carga la sesión desde archivo cifrado

        Returns:
            True si se cargó exitosamente, False en caso contrario
        """
        if not SESSION_FILE.exists():
            return False

        try:
            if self._cipher:
                # Descifrar datos
                encrypted_data = SESSION_FILE.read_bytes()
                json_data = self._cipher.decrypt(encrypted_data).decode()
            else:
                # Fallback sin cifrado
                json_data = SESSION_FILE.read_text()

            data = json.loads(json_data)

            # Verificar si el token ha expirado
            expires_at = datetime.fromisoformat(data["token_expires_at"]) if data.get("token_expires_at") else None

            if expires_at and datetime.now() >= expires_at:
                # Token expirado, intentar con refresh token si existe
                if not data.get("refresh_token"):
                    self.delete_session_file()
                    return False

            # Restaurar sesión
            self._user_id = data["user_id"]
            self._username = data["username"]
            self._email = data["email"]
            self._nombre_completo = data["nombre_completo"]
            self._role = data["role"]
            self._access_token = data["access_token"]
            self._refresh_token = data.get("refresh_token")
            self._token_expires_at = expires_at
            self._is_authenticated = True

            return True
        except Exception as e:
            print(f"Error al cargar sesión: {e}")
            self.delete_session_file()
            return False

    def delete_session_file(self):
        """Elimina el archivo de sesión"""
        try:
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
        except Exception as e:
            print(f"Error al eliminar archivo de sesión: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Retorna la sesión como diccionario"""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "email": self._email,
            "nombre_completo": self._nombre_completo,
            "role": self._role,
            "is_authenticated": self._is_authenticated,
        }
