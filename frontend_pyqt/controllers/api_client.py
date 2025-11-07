"""
Cliente HTTP para comunicación con el backend FastAPI
Maneja autenticación JWT, refresh automático de tokens y errores HTTP
"""
import httpx
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from resources.constants import API_BASE_URL, REQUEST_TIMEOUT, APIEndpoints
from controllers.user_state import UserState
from controllers.errors import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NetworkError,
    NotFoundError,
    AppException
)


class APIClient:
    """Cliente HTTP para comunicación con el backend"""

    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = REQUEST_TIMEOUT
        self.user_state = UserState()

    def _get_url(self, endpoint: str) -> str:
        """Construye la URL completa"""
        return urljoin(self.base_url, endpoint)

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Obtiene los headers para las requests

        Args:
            include_auth: Si incluir el token de autenticación

        Returns:
            Diccionario de headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if include_auth and self.user_state.is_authenticated():
            headers["Authorization"] = f"Bearer {self.user_state.access_token}"

        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        """
        Maneja la respuesta HTTP y lanza excepciones apropiadas

        Args:
            response: Respuesta HTTP de httpx

        Returns:
            JSON parseado de la respuesta

        Raises:
            Varias excepciones según el código de estado
        """
        if response.status_code == 200 or response.status_code == 201:
            return response.json() if response.content else {}

        # Manejar errores
        try:
            error_data = response.json()
            error_message = error_data.get("detail", "Error desconocido")
        except Exception:
            error_message = response.text or f"Error HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(error_message)
        elif response.status_code == 403:
            raise AuthorizationError(error_message)
        elif response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 422:
            raise ValidationError(error_message)
        elif response.status_code >= 500:
            raise AppException(f"Error del servidor: {error_message}", response.status_code)
        else:
            raise AppException(error_message, response.status_code)

    async def _refresh_token_if_needed(self):
        """Refresca el token si es necesario antes de hacer una request"""
        if self.user_state.needs_refresh() and self.user_state.refresh_token:
            try:
                await self.refresh_token()
            except Exception:
                # Si falla el refresh, limpiar sesión
                self.user_state.clear_session()
                raise AuthenticationError("Sesión expirada. Por favor, inicie sesión nuevamente.")

    # Métodos HTTP base
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        include_auth: bool = True
    ) -> Any:
        """
        Realiza una petición GET

        Args:
            endpoint: Endpoint de la API
            params: Parámetros de query
            include_auth: Si incluir autenticación

        Returns:
            Respuesta JSON parseada
        """
        if include_auth:
            await self._refresh_token_if_needed()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self._get_url(endpoint),
                    headers=self._get_headers(include_auth),
                    params=params
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        include_auth: bool = True
    ) -> Any:
        """
        Realiza una petición POST

        Args:
            endpoint: Endpoint de la API
            data: Datos a enviar en el body
            include_auth: Si incluir autenticación

        Returns:
            Respuesta JSON parseada
        """
        if include_auth:
            await self._refresh_token_if_needed()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._get_url(endpoint),
                    headers=self._get_headers(include_auth),
                    json=data
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        include_auth: bool = True
    ) -> Any:
        """
        Realiza una petición PUT

        Args:
            endpoint: Endpoint de la API
            data: Datos a enviar en el body
            include_auth: Si incluir autenticación

        Returns:
            Respuesta JSON parseada
        """
        if include_auth:
            await self._refresh_token_if_needed()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    self._get_url(endpoint),
                    headers=self._get_headers(include_auth),
                    json=data
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    async def delete(
        self,
        endpoint: str,
        include_auth: bool = True
    ) -> Any:
        """
        Realiza una petición DELETE

        Args:
            endpoint: Endpoint de la API
            include_auth: Si incluir autenticación

        Returns:
            Respuesta JSON parseada
        """
        if include_auth:
            await self._refresh_token_if_needed()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    self._get_url(endpoint),
                    headers=self._get_headers(include_auth)
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    # Métodos de autenticación
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Inicia sesión

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            Datos del usuario y tokens
        """
        # FastAPI OAuth2 espera form data
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._get_url(APIEndpoints.LOGIN),
                    data={
                        "username": username,
                        "password": password
                    }
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    async def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra un nuevo usuario

        Args:
            user_data: Datos del usuario a registrar

        Returns:
            Datos del usuario creado
        """
        return await self.post(APIEndpoints.REGISTER, user_data, include_auth=False)

    async def refresh_token(self) -> Dict[str, Any]:
        """
        Refresca el token de acceso

        Returns:
            Nuevo access token
        """
        if not self.user_state.refresh_token:
            raise AuthenticationError("No hay refresh token disponible")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._get_url(APIEndpoints.REFRESH),
                    headers={
                        "Authorization": f"Bearer {self.user_state.refresh_token}"
                    }
                )
                data = self._handle_response(response)

                # Actualizar tokens en el estado
                self.user_state.update_tokens(
                    access_token=data["access_token"],
                    expires_in=data.get("expires_in", 900)
                )

                return data
        except httpx.RequestError as e:
            raise NetworkError(f"Error de conexión: {str(e)}")

    async def logout(self):
        """Cierra sesión"""
        try:
            await self.post(APIEndpoints.LOGOUT, include_auth=True)
        except Exception:
            pass  # Ignorar errores de logout
        finally:
            self.user_state.clear_session()
            self.user_state.delete_session_file()

    async def get_current_user(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual"""
        return await self.get(APIEndpoints.ME)

    # Métodos para usuarios
    async def get_users(self, skip: int = 0, limit: int = 100) -> list:
        """Obtiene lista de usuarios"""
        return await self.get(APIEndpoints.USERS, params={"skip": skip, "limit": limit})

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Obtiene un usuario por ID"""
        endpoint = APIEndpoints.USERS_BY_ID.format(user_id=user_id)
        return await self.get(endpoint)

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un usuario"""
        endpoint = APIEndpoints.USERS_BY_ID.format(user_id=user_id)
        return await self.put(endpoint, user_data)

    # Métodos admin
    async def approve_user(self, user_id: int) -> Dict[str, Any]:
        """Aprueba un usuario (solo admin)"""
        endpoint = APIEndpoints.ADMIN_APPROVE_USER.format(user_id=user_id)
        return await self.post(endpoint)

    async def toggle_user_active(self, user_id: int) -> Dict[str, Any]:
        """Activa/desactiva un usuario (solo admin)"""
        endpoint = APIEndpoints.ADMIN_TOGGLE_USER.format(user_id=user_id)
        return await self.post(endpoint)

    # Métodos para pacientes
    async def get_pacientes(self, skip: int = 0, limit: int = 100) -> list:
        """Obtiene lista de pacientes"""
        return await self.get(APIEndpoints.PACIENTES, params={"skip": skip, "limit": limit})

    async def get_paciente(self, paciente_id: int) -> Dict[str, Any]:
        """Obtiene un paciente por ID"""
        endpoint = APIEndpoints.PACIENTES_BY_ID.format(paciente_id=paciente_id)
        return await self.get(endpoint)

    async def create_paciente(self, paciente_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo paciente"""
        return await self.post(APIEndpoints.PACIENTES, paciente_data)

    async def update_paciente(self, paciente_id: int, paciente_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un paciente"""
        endpoint = APIEndpoints.PACIENTES_BY_ID.format(paciente_id=paciente_id)
        return await self.put(endpoint, paciente_data)

    async def delete_paciente(self, paciente_id: int):
        """Elimina un paciente"""
        endpoint = APIEndpoints.PACIENTES_BY_ID.format(paciente_id=paciente_id)
        return await self.delete(endpoint)

    # Métodos para boxes
    async def get_boxes(self, skip: int = 0, limit: int = 100) -> list:
        """Obtiene lista de boxes"""
        return await self.get(APIEndpoints.BOXES, params={"skip": skip, "limit": limit})

    async def get_box(self, box_id: int) -> Dict[str, Any]:
        """Obtiene un box por ID"""
        endpoint = APIEndpoints.BOXES_BY_ID.format(box_id=box_id)
        return await self.get(endpoint)

    async def create_box(self, box_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo box"""
        return await self.post(APIEndpoints.BOXES, box_data)

    async def update_box(self, box_id: int, box_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un box"""
        endpoint = APIEndpoints.BOXES_BY_ID.format(box_id=box_id)
        return await self.put(endpoint, box_data)

    async def delete_box(self, box_id: int):
        """Elimina un box"""
        endpoint = APIEndpoints.BOXES_BY_ID.format(box_id=box_id)
        return await self.delete(endpoint)

    # Métodos para atenciones
    async def get_atenciones(self, skip: int = 0, limit: int = 100) -> list:
        """Obtiene lista de atenciones"""
        return await self.get(APIEndpoints.ATENCIONES, params={"skip": skip, "limit": limit})

    async def get_atencion(self, atencion_id: int) -> Dict[str, Any]:
        """Obtiene una atención por ID"""
        endpoint = APIEndpoints.ATENCIONES_BY_ID.format(atencion_id=atencion_id)
        return await self.get(endpoint)

    async def create_atencion(self, atencion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva atención"""
        return await self.post(APIEndpoints.ATENCIONES, atencion_data)

    async def update_atencion(self, atencion_id: int, atencion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una atención"""
        endpoint = APIEndpoints.ATENCIONES_BY_ID.format(atencion_id=atencion_id)
        return await self.put(endpoint, atencion_data)

    async def get_atenciones_profesional(self) -> list:
        """Obtiene atenciones del profesional actual"""
        return await self.get(APIEndpoints.ATENCIONES_PROFESIONAL)
