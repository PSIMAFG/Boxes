"""
Sistema de logging estructurado en JSON.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from app.config.settings import settings


class JSONFormatter(logging.Formatter):
    """Formateador que convierte logs a JSON estructurado"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Agregar extras si existen
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "rol"):
            log_data["rol"] = record.rol
        if hasattr(record, "event"):
            log_data["event"] = record.event
        if hasattr(record, "extra_data"):
            log_data["extra_data"] = record.extra_data

        # Agregar exception info si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formateador de texto plano para desarrollo"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging():
    """Configura el sistema de logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Crear handler para stdout
    handler = logging.StreamHandler(sys.stdout)

    # Seleccionar formateador según configuración
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Si hay archivo de log configurado, agregar file handler
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger por nombre"""
    return logging.getLogger(name)


class StructuredLogger:
    """
    Logger que facilita logging estructurado con campos extras.

    Usage:
        logger = StructuredLogger("app.servicios")
        logger.info(
            "Usuario creado",
            event="usuario_creado",
            user_id="123",
            extra_data={"nombre": "Juan"}
        )
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        msg: str,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        rol: Optional[str] = None,
        event: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        extra = {}
        if request_id:
            extra["request_id"] = request_id
        if user_id:
            extra["user_id"] = user_id
        if rol:
            extra["rol"] = rol
        if event:
            extra["event"] = event
        if extra_data:
            extra["extra_data"] = extra_data

        self.logger.log(level, msg, extra=extra, exc_info=exc_info)

    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)


# Configurar logging al importar
setup_logging()
