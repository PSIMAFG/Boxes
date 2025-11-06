.PHONY: help install test lint format run migrate seed docker-up docker-down clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install     - Instalar dependencias con Poetry"
	@echo "  make test        - Ejecutar tests con cobertura"
	@echo "  make lint        - Ejecutar linters (ruff + mypy)"
	@echo "  make format      - Formatear código (black + ruff)"
	@echo "  make run         - Ejecutar API en modo desarrollo"
	@echo "  make migrate     - Aplicar migraciones de BD"
	@echo "  make seed        - Poblar datos iniciales"
	@echo "  make docker-up   - Levantar con Docker Compose"
	@echo "  make docker-down - Detener Docker Compose"
	@echo "  make clean       - Limpiar archivos temporales"

install:
	poetry install

test:
	poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint:
	poetry run ruff check app/
	poetry run mypy app/

format:
	poetry run black app/
	poetry run ruff check --fix app/

run:
	poetry run uvicorn app.presentacion.api_rest.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	poetry run alembic upgrade head

seed:
	poetry run python -m app.scripts.seed_data

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
