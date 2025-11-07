"""
Manejo de errores y excepciones personalizadas
"""
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QWidget


class AppException(Exception):
    """Excepción base de la aplicación"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Error de autenticación"""
    def __init__(self, message: str = "Error de autenticación"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppException):
    """Error de autorización (permisos)"""
    def __init__(self, message: str = "No tiene permisos para esta acción"):
        super().__init__(message, status_code=403)


class ValidationError(AppException):
    """Error de validación de datos"""
    def __init__(self, message: str = "Error de validación"):
        super().__init__(message, status_code=422)


class NetworkError(AppException):
    """Error de red/conexión"""
    def __init__(self, message: str = "Error de conexión"):
        super().__init__(message, status_code=None)


class NotFoundError(AppException):
    """Recurso no encontrado"""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404)


class ErrorHandler:
    """Manejador centralizado de errores con diálogos visuales"""

    @staticmethod
    def show_error(parent: Optional[QWidget], title: str, message: str):
        """Muestra un diálogo de error"""
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str):
        """Muestra un diálogo de advertencia"""
        QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_info(parent: Optional[QWidget], title: str, message: str):
        """Muestra un diálogo informativo"""
        QMessageBox.information(parent, title, message)

    @staticmethod
    def show_success(parent: Optional[QWidget], title: str, message: str):
        """Muestra un diálogo de éxito"""
        QMessageBox.information(parent, title, message)

    @staticmethod
    def handle_exception(parent: Optional[QWidget], exception: Exception):
        """Maneja una excepción y muestra el diálogo apropiado"""
        if isinstance(exception, AuthenticationError):
            ErrorHandler.show_error(
                parent,
                "Error de Autenticación",
                exception.message
            )
        elif isinstance(exception, AuthorizationError):
            ErrorHandler.show_error(
                parent,
                "Permisos Insuficientes",
                exception.message
            )
        elif isinstance(exception, ValidationError):
            ErrorHandler.show_warning(
                parent,
                "Error de Validación",
                exception.message
            )
        elif isinstance(exception, NetworkError):
            ErrorHandler.show_error(
                parent,
                "Error de Conexión",
                exception.message
            )
        elif isinstance(exception, NotFoundError):
            ErrorHandler.show_warning(
                parent,
                "No Encontrado",
                exception.message
            )
        elif isinstance(exception, AppException):
            ErrorHandler.show_error(
                parent,
                "Error",
                exception.message
            )
        else:
            ErrorHandler.show_error(
                parent,
                "Error Inesperado",
                f"Ha ocurrido un error: {str(exception)}"
            )

    @staticmethod
    def confirm(parent: Optional[QWidget], title: str, message: str) -> bool:
        """Muestra un diálogo de confirmación"""
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
