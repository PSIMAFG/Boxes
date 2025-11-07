"""
Controlador de autenticación
Maneja login, registro, refresh y logout
"""
from typing import Dict, Any, Optional
from controllers.api_client import APIClient
from controllers.user_state import UserState
from controllers.errors import AuthenticationError


class AuthController:
    """Controlador para operaciones de autenticación"""

    def __init__(self):
        self.api_client = APIClient()
        self.user_state = UserState()

    async def login(self, username: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """
        Inicia sesión de usuario

        Args:
            username: Nombre de usuario
            password: Contraseña
            remember_me: Si guardar la sesión persistentemente

        Returns:
            Datos del usuario autenticado

        Raises:
            AuthenticationError: Si las credenciales son inválidas
        """
        # Llamar al endpoint de login
        response = await self.api_client.login(username, password)

        # Extraer tokens y datos de usuario
        access_token = response.get("access_token")
        refresh_token = response.get("refresh_token")
        token_type = response.get("token_type", "bearer")
        expires_in = response.get("expires_in", 900)  # 15 minutos por defecto

        if not access_token:
            raise AuthenticationError("Respuesta de login inválida")

        # Obtener información del usuario
        user_data = response.get("user", {})

        # Validar estado del usuario
        estado = user_data.get("estado")
        if estado != "APROBADO":
            raise AuthenticationError(
                f"Usuario no aprobado. Estado actual: {estado}. "
                "Contacte al administrador."
            )

        # Actualizar el estado de sesión
        self.user_state.set_session(
            user_id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email"),
            nombre_completo=user_data.get("nombre_completo"),
            role=user_data.get("role"),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in
        )

        # Guardar sesión si se solicitó
        if remember_me:
            self.user_state.save_to_file(remember_me=True)

        return user_data

    async def register(
        self,
        username: str,
        password: str,
        email: str,
        nombre_completo: str,
        rut: str,
        role: str,
        telefono: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra un nuevo usuario

        Args:
            username: Nombre de usuario
            password: Contraseña
            email: Email
            nombre_completo: Nombre completo
            rut: RUT del usuario
            role: Rol solicitado
            telefono: Teléfono opcional

        Returns:
            Datos del usuario registrado

        Raises:
            ValidationError: Si los datos son inválidos
            AppException: Si hay un error en el registro
        """
        user_data = {
            "username": username,
            "password": password,
            "email": email,
            "nombre_completo": nombre_completo,
            "rut": rut,
            "role": role,
        }

        if telefono:
            user_data["telefono"] = telefono

        response = await self.api_client.register(user_data)
        return response

    async def logout(self):
        """
        Cierra sesión del usuario

        Limpia el estado y elimina la sesión persistente
        """
        await self.api_client.logout()

    async def refresh_session(self) -> bool:
        """
        Refresca la sesión si es posible

        Returns:
            True si se refrescó exitosamente, False en caso contrario
        """
        try:
            if self.user_state.refresh_token:
                await self.api_client.refresh_token()
                return True
        except Exception:
            pass

        return False

    async def restore_session(self) -> bool:
        """
        Intenta restaurar una sesión guardada

        Returns:
            True si se restauró exitosamente, False en caso contrario
        """
        # Cargar sesión desde archivo
        if not self.user_state.load_from_file():
            return False

        # Verificar si necesita refresh
        if self.user_state.needs_refresh():
            return await self.refresh_session()

        return True

    async def get_current_user(self) -> Dict[str, Any]:
        """
        Obtiene información del usuario actual desde el backend

        Returns:
            Datos actualizados del usuario
        """
        return await self.api_client.get_current_user()

    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.user_state.is_authenticated()

    def get_user_info(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual desde el estado"""
        return self.user_state.to_dict()
