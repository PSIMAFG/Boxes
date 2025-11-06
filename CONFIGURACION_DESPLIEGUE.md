# Configuración y Despliegue

## config/settings.py

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./agenda_clinica.db"
    
    # Security
    SECRET_KEY: str = "cambiar-en-produccion-usar-secreto-muy-seguro"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRATION_HOURS: int = 8
    BCRYPT_ROUNDS: int = 12
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Application
    APP_NAME: str = "Agenda Clínica API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    # ML Models
    MODELS_PATH: str = "./modelos"
    RETRAIN_SCHEDULE: str = "0 2 * * 0"  # Domingos 2 AM (cron format)
    ENABLE_ML_SCORING: bool = True
    MIN_TRAINING_SAMPLES: int = 500
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 300
    ENABLE_CACHE: bool = False
    
    # Feature Flags
    ENABLE_ALERTAS_AUTOMATICAS: bool = True
    ENABLE_AUDITORIA: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
```

---

## .env.example

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agenda_clinica

# Security - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=super-secreto-cambiar-en-produccion-usar-64-caracteres-aleatorios
ALGORITHM=HS256
TOKEN_EXPIRATION_HOURS=8
BCRYPT_ROUNDS=12

# CORS - Dominios permitidos
CORS_ORIGINS=["http://localhost:3000","https://app.clinica.cl"]

# Application
APP_NAME=Agenda Clínica API
APP_VERSION=1.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# ML Models
MODELS_PATH=/app/modelos
RETRAIN_SCHEDULE="0 2 * * 0"
ENABLE_ML_SCORING=true
MIN_TRAINING_SAMPLES=500

# Cache (Redis)
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=300
ENABLE_CACHE=true

# Feature Flags
ENABLE_ALERTAS_AUTOMATICAS=true
ENABLE_AUDITORIA=true

# Pagination
DEFAULT_PAGE_SIZE=50
MAX_PAGE_SIZE=100
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

LABEL maintainer="dev@clinica.cl"
LABEL description="Sistema de Agenda Clínica con ML"

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==1.7.0

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock ./

# Configurar Poetry para no crear virtualenv
RUN poetry config virtualenvs.create false

# Instalar dependencias de producción
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiar código de la aplicación
COPY . .

# Crear directorio para modelos ML
RUN mkdir -p /app/modelos

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "app.presentacion.api_rest.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: agenda_clinica_db
    environment:
      POSTGRES_DB: agenda_clinica
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - agenda_network

  redis:
    image: redis:7-alpine
    container_name: agenda_clinica_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - agenda_network

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: agenda_clinica_api
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/agenda_clinica
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-secreto-cambiar-en-produccion}
      ENVIRONMENT: ${ENVIRONMENT:-development}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      ENABLE_ML_SCORING: ${ENABLE_ML_SCORING:-true}
      ENABLE_CACHE: ${ENABLE_CACHE:-true}
    volumes:
      - ./app:/app/app
      - ./modelos:/app/modelos
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.presentacion.api_rest.main:app --host 0.0.0.0 --port 8000 --reload"
    networks:
      - agenda_network

volumes:
  postgres_data:
  redis_data:

networks:
  agenda_network:
    driver: bridge
```

---

## docker-compose.prod.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: agenda_clinica_db_prod
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - agenda_network_prod

  redis:
    image: redis:7-alpine
    container_name: agenda_clinica_redis_prod
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data_prod:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - agenda_network_prod

  api:
    image: agenda-clinica-api:latest
    container_name: agenda_clinica_api_prod
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
      LOG_LEVEL: INFO
      DEBUG: false
      ENABLE_ML_SCORING: true
      ENABLE_CACHE: true
    volumes:
      - ./modelos:/app/modelos
      - ./logs:/app/logs
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.presentacion.api_rest.main:app --host 0.0.0.0 --port 8000 --workers 4"
    restart: unless-stopped
    networks:
      - agenda_network_prod

  nginx:
    image: nginx:alpine
    container_name: agenda_clinica_nginx
    depends_on:
      - api
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    restart: unless-stopped
    networks:
      - agenda_network_prod

volumes:
  postgres_data_prod:
  redis_data_prod:

networks:
  agenda_network_prod:
    driver: bridge
```

---

## Makefile

```makefile
.PHONY: help install test lint format run migrate seed clean docker-up docker-down docker-logs

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instalar dependencias con Poetry"
	@echo "  make test          - Ejecutar tests con cobertura"
	@echo "  make test-unit     - Ejecutar solo tests unitarios"
	@echo "  make test-int      - Ejecutar solo tests de integración"
	@echo "  make lint          - Ejecutar linters (ruff + mypy)"
	@echo "  make format        - Formatear código (black + ruff)"
	@echo "  make run           - Ejecutar API en modo desarrollo"
	@echo "  make run-ui        - Ejecutar UI PyQt6"
	@echo "  make migrate       - Aplicar migraciones pendientes"
	@echo "  make migrate-create - Crear nueva migración"
	@echo "  make seed          - Poblar datos iniciales"
	@echo "  make clean         - Limpiar archivos generados"
	@echo "  make docker-up     - Levantar con Docker Compose"
	@echo "  make docker-down   - Detener Docker Compose"
	@echo "  make docker-logs   - Ver logs de Docker"
	@echo "  make docker-build  - Construir imagen Docker"

install:
	poetry install

test:
	poetry run pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

test-unit:
	poetry run pytest tests/unit/ -v

test-int:
	poetry run pytest tests/integration/ -v

lint:
	poetry run ruff check app/
	poetry run mypy app/

format:
	poetry run black app/ tests/
	poetry run ruff check --fix app/

run:
	poetry run uvicorn app.presentacion.api_rest.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	poetry run python -m app.presentacion.ui_escritorio.main

migrate:
	poetry run alembic upgrade head

migrate-create:
	@read -p "Nombre de la migración: " name; \
	poetry run alembic revision --autogenerate -m "$$name"

migrate-rollback:
	poetry run alembic downgrade -1

seed:
	poetry run python -m app.scripts.seed_data

seed-test:
	poetry run python -m app.scripts.seed_test_data

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-build:
	docker build -t agenda-clinica-api:latest .

docker-restart:
	docker-compose restart api

docker-shell:
	docker-compose exec api /bin/bash

docker-db-shell:
	docker-compose exec db psql -U postgres -d agenda_clinica

backup-db:
	docker-compose exec -T db pg_dump -U postgres agenda_clinica | gzip > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql.gz

restore-db:
	@read -p "Archivo de backup (ej: backup_20250115_100000.sql.gz): " file; \
	gunzip -c backups/$$file | docker-compose exec -T db psql -U postgres agenda_clinica

train-ml:
	poetry run python -m app.scripts.train_models

quality:
	@echo "Ejecutando checks de calidad..."
	@make lint
	@make test
	@echo "Checks de calidad completados"
```

---

## pyproject.toml

```toml
[tool.poetry]
name = "agenda-clinica"
version = "1.0.0"
description = "Sistema de gestión de agenda clínica con asignación dinámica y analítica ML"
authors = ["Equipo Desarrollo <dev@clinica.cl>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.25"
alembic = "^1.13.1"
pydantic = {extras = ["email"], version = "^2.5.3"}
pydantic-settings = "^2.1.0"
psycopg2-binary = "^2.9.9"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
PyQt6 = "^6.6.1"
pandas = "^2.1.4"
scikit-learn = "^1.4.0"
joblib = "^1.3.2"
structlog = "^24.1.0"
prometheus-client = "^0.19.0"
redis = "^5.0.1"
httpx = "^0.26.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.23.3"
black = "^24.1.1"
ruff = "^0.1.14"
mypy = "^1.8.0"
faker = "^22.2.0"
ipython = "^8.20.0"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.ruff_cache
  | \.venv
  | _build
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = ["E501", "B008", "B904"]
target-version = "py311"
exclude = [
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "alembic/versions/*.py",
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
exclude = [
    "alembic/",
    "tests/",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80"
markers = [
    "unit: Tests unitarios",
    "integration: Tests de integración",
    "slow: Tests lentos",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## nginx.conf (Producción)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        least_conn;
        server api_1:8000;
        server api_2:8000;
    }

    server {
        listen 80;
        server_name api.clinica.cl;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.clinica.cl;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        client_max_body_size 10M;

        # Logging
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        # API routes
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://api;
            access_log off;
        }

        # Metrics (protegido)
        location /metrics {
            deny all;
            return 403;
        }
    }
}
```

---

## Scripts de Deployment

### scripts/deploy.sh

```bash
#!/bin/bash
set -e

echo "Iniciando deployment..."

# Variables
ENVIRONMENT=${1:-production}
VERSION=$(git rev-parse --short HEAD)

echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"

# Build imagen
echo "Building Docker image..."
docker build -t agenda-clinica-api:$VERSION .
docker tag agenda-clinica-api:$VERSION agenda-clinica-api:latest

# Backup de BD antes de migraciones
echo "Backing up database..."
make backup-db

# Aplicar migraciones
echo "Running migrations..."
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Deploy
echo "Deploying containers..."
docker-compose -f docker-compose.prod.yml up -d

# Verificar health
echo "Checking health..."
sleep 10
curl -f http://localhost:8000/health || exit 1

echo "Deployment completado exitosamente"
```

### scripts/backup.sh

```bash
#!/bin/bash
set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

echo "Iniciando backup de base de datos..."
docker-compose exec -T db pg_dump -U postgres agenda_clinica | gzip > $BACKUP_FILE

echo "Backup completado: $BACKUP_FILE"

# Limpiar backups antiguos (mantener últimos 30 días)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backups antiguos eliminados"
```

### scripts/seed_data.py

```python
#!/usr/bin/env python3
"""Script para poblar datos iniciales en la base de datos"""

from app.infraestructura.db.session import SessionLocal
from app.infraestructura.repos.usuario_repo import UsuarioRepoSQL
from app.infraestructura.repos.profesional_repo import ProfesionalRepoSQL
from app.infraestructura.repos.box_repo import BoxRepoSQL
from app.infraestructura.repos.prestacion_repo import PrestacionRepoSQL
from app.infraestructura.repos.auth_repo import AuthRepoSQL
from app.dominio.entidades import (
    Usuario, Profesional, Box, Prestacion, UsuarioSistema
)
from app.dominio.valores import RUT
from app.infraestructura.seguridad.password_hasher import hash_password
from datetime import date


def seed():
    session = SessionLocal()
    
    try:
        # Usuarios del sistema
        print("Creando usuarios del sistema...")
        auth_repo = AuthRepoSQL(session)
        
        admin = UsuarioSistema(
            email="admin@clinica.cl",
            password_hash=hash_password("admin123"),
            rol="admin"
        )
        auth_repo.crear_usuario_sistema(admin)
        
        recepcion = UsuarioSistema(
            email="recepcion@clinica.cl",
            password_hash=hash_password("recepcion123"),
            rol="recepcion"
        )
        auth_repo.crear_usuario_sistema(recepcion)
        
        # Boxes
        print("Creando boxes...")
        box_repo = BoxRepoSQL(session)
        
        box1 = Box(nombre="Box 1", ubicacion="Primer piso")
        box2 = Box(nombre="Box 2", ubicacion="Primer piso")
        box3 = Box(nombre="Box 3", ubicacion="Segundo piso")
        
        box_repo.crear(box1)
        box_repo.crear(box2)
        box_repo.crear(box3)
        
        # Profesionales
        print("Creando profesionales...")
        prof_repo = ProfesionalRepoSQL(session)
        
        kine = Profesional(nombre="Dra. Ana López", profesion="Kinesióloga")
        fono = Profesional(nombre="Dr. Carlos Ruiz", profesion="Fonoaudiólogo")
        
        prof_repo.crear(kine)
        prof_repo.crear(fono)
        
        # Prestaciones
        print("Creando prestaciones...")
        prest_repo = PrestacionRepoSQL(session)
        
        kinesiologia = Prestacion(
            nombre="Kinesiología",
            duracion_minutos=45,
            periodicidad_dias=30,
            tolerancia_dias=7
        )
        
        fonoaudiologia = Prestacion(
            nombre="Fonoaudiología",
            duracion_minutos=60,
            periodicidad_dias=21,
            tolerancia_dias=5
        )
        
        prest_repo.crear(kinesiologia)
        prest_repo.crear(fonoaudiologia)
        
        # Usuarios pacientes
        print("Creando usuarios pacientes...")
        usuario_repo = UsuarioRepoSQL(session)
        
        usuario1 = Usuario(
            rut=RUT("12345678-5"),
            nombre="Juan Pérez González",
            fecha_nacimiento=date(1980, 5, 15),
            nivel_apoyo=2
        )
        
        usuario2 = Usuario(
            rut=RUT("98765432-1"),
            nombre="María González Silva",
            fecha_nacimiento=date(1975, 8, 20),
            nivel_apoyo=1
        )
        
        usuario_repo.crear(usuario1)
        usuario_repo.crear(usuario2)
        
        session.commit()
        print("Datos iniciales creados exitosamente")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
```

---

## Comandos de Uso

### Desarrollo Local

```bash
# Instalar dependencias
make install

# Aplicar migraciones
make migrate

# Poblar datos iniciales
make seed

# Ejecutar API
make run

# Ejecutar tests
make test

# Formatear código
make format
```

### Docker

```bash
# Levantar servicios
make docker-up

# Ver logs
make docker-logs

# Detener servicios
make docker-down

# Backup de BD
make backup-db

# Shell en contenedor
make docker-shell
```

### Producción

```bash
# Build y deploy
./scripts/deploy.sh production

# Backup
./scripts/backup.sh

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f api
```
