"""
Configuración del sistema usando Pydantic Settings.
Variables de entorno cargadas desde .env
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Aplicación
    APP_NAME: str = "Sistema de Agenda Clínica"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Base de datos
    DATABASE_URL: str = Field(
        default="sqlite:///./agenda_clinica.db",
        description="URL de conexión a la base de datos"
    )
    DB_ECHO: bool = False  # Log de SQL queries

    # Seguridad
    SECRET_KEY: str = Field(
        default="CHANGE-THIS-SECRET-KEY-IN-PRODUCTION",
        description="Clave secreta para JWT"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8
    BCRYPT_ROUNDS: int = 12

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Orígenes permitidos para CORS"
    )

    # API
    API_PREFIX: str = "/api/v1"
    DOCS_ENABLED: bool = True

    # Machine Learning
    ENABLE_ML_SCORING: bool = False
    ML_MODELS_PATH: str = "./models"
    ML_RETRAIN_INTERVAL_DAYS: int = 7

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json o text
    LOG_FILE: Optional[str] = None

    # Redis (opcional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 3600

    # Alertas
    ALERTAS_PREVENTIVAS_DIAS: int = 7  # Días antes de fecha objetivo

    # Paginación
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
