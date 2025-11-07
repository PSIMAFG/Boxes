"""
Constantes globales del Frontend PyQt6 - Sistema de Agenda Clínica
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
UI_DIR = BASE_DIR / "ui"
CONTROLLERS_DIR = BASE_DIR / "controllers"

# Configuración de la API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Configuración de la aplicación
APP_NAME = os.getenv("APP_NAME", "Sistema de Agenda Clínica")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Archivo de sesión
SESSION_FILE = BASE_DIR / os.getenv("SESSION_FILE", ".session.enc")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

# Endpoints de la API
class APIEndpoints:
    """Endpoints del backend FastAPI"""
    # Autenticación
    LOGIN = "/auth/login"
    REGISTER = "/auth/register"
    REFRESH = "/auth/refresh"
    LOGOUT = "/auth/logout"
    ME = "/auth/me"

    # Usuarios
    USERS = "/usuarios"
    USERS_BY_ID = "/usuarios/{user_id}"

    # Admin
    ADMIN_USERS = "/admin/users"
    ADMIN_APPROVE_USER = "/admin/users/{user_id}/approve"
    ADMIN_TOGGLE_USER = "/admin/users/{user_id}/toggle"

    # Pacientes
    PACIENTES = "/pacientes"
    PACIENTES_BY_ID = "/pacientes/{paciente_id}"

    # Boxes
    BOXES = "/boxes"
    BOXES_BY_ID = "/boxes/{box_id}"

    # Atenciones
    ATENCIONES = "/atenciones"
    ATENCIONES_BY_ID = "/atenciones/{atencion_id}"
    ATENCIONES_PROFESIONAL = "/atenciones/profesional/me"

    # Reportes
    REPORTES_GENERAL = "/reportes/general"
    REPORTES_PROFESIONAL = "/reportes/profesional/{profesional_id}"

# Roles del sistema
class Roles:
    """Roles definidos en RBAC"""
    ADMIN = "admin"
    PROFESIONAL = "profesional"
    ADMINISTRATIVO = "administrativo"

    ALL = [ADMIN, PROFESIONAL, ADMINISTRATIVO]

    DISPLAY_NAMES = {
        ADMIN: "Administrador",
        PROFESIONAL: "Profesional",
        ADMINISTRATIVO: "Administrativo"
    }

# Estados de usuario
class UserStatus:
    """Estados de aprobación de usuario"""
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

    DISPLAY_NAMES = {
        PENDIENTE: "Pendiente de Aprobación",
        APROBADO: "Aprobado",
        RECHAZADO: "Rechazado"
    }

# Configuración de tokens JWT
TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7

# Mensajes de error comunes
class ErrorMessages:
    """Mensajes de error estandarizados"""
    NETWORK_ERROR = "Error de conexión. Verifique su conexión a internet."
    UNAUTHORIZED = "Credenciales inválidas o sesión expirada."
    FORBIDDEN = "No tiene permisos para realizar esta acción."
    NOT_FOUND = "Recurso no encontrado."
    VALIDATION_ERROR = "Error de validación. Verifique los datos ingresados."
    SERVER_ERROR = "Error interno del servidor. Intente más tarde."
    UNKNOWN_ERROR = "Error desconocido. Contacte al administrador."

# Configuración de UI
class UIConfig:
    """Configuración de la interfaz de usuario"""
    WINDOW_MIN_WIDTH = 1024
    WINDOW_MIN_HEIGHT = 768

    # Colores principales
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#FFC107"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#F44336"
    WARNING_COLOR = "#FF9800"

    # Fuentes
    FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 14
