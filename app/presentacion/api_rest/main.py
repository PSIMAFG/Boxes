"""
Aplicación principal de la API REST con FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.infraestructura.db.database import engine
from app.infraestructura.db.models import Base

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Healthchecks
@app.get("/health")
async def health_check():
    """Health check básico"""
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health/db")
async def health_db():
    """Health check de base de datos"""
    try:
        # Test simple de conexión
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}


# Importar y registrar routers
from app.presentacion.api_rest.routers import (
    auth_router,
    usuarios_router,
    profesionales_router,
    boxes_router,
    prestaciones_router,
    citas_router,
    alertas_router,
    analitica_router,
)

app.include_router(auth_router.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(usuarios_router.router, prefix=f"{settings.API_PREFIX}/usuarios", tags=["usuarios"])
app.include_router(profesionales_router.router, prefix=f"{settings.API_PREFIX}/profesionales", tags=["profesionales"])
app.include_router(boxes_router.router, prefix=f"{settings.API_PREFIX}/boxes", tags=["boxes"])
app.include_router(prestaciones_router.router, prefix=f"{settings.API_PREFIX}/prestaciones", tags=["prestaciones"])
app.include_router(citas_router.router, prefix=f"{settings.API_PREFIX}/citas", tags=["citas"])
app.include_router(alertas_router.router, prefix=f"{settings.API_PREFIX}/alertas", tags=["alertas"])
app.include_router(analitica_router.router, prefix=f"{settings.API_PREFIX}/analitica", tags=["analitica"])


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    from app.infraestructura.logging.logger import get_logger
    logger = get_logger("app.main")
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de apagado de la aplicación"""
    from app.infraestructura.logging.logger import get_logger
    logger = get_logger("app.main")
    logger.info(f"Apagando {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.presentacion.api_rest.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
