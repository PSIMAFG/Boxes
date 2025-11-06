"""
Configuración de la base de datos y gestión de sesiones.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from app.config.settings import settings


# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para FastAPI que proporciona una sesión de BD.
    Se cierra automáticamente al finalizar la request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager para obtener sesión de BD.
    Útil fuera de FastAPI.

    Usage:
        with get_db_context() as db:
            # usar db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Solo usar en desarrollo. En producción usar Alembic.
    """
    from app.infraestructura.db.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Elimina todas las tablas.
    PELIGRO: Solo usar en desarrollo/testing.
    """
    from app.infraestructura.db.models import Base
    Base.metadata.drop_all(bind=engine)
