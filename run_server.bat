@echo off
REM Script para iniciar el servidor FastAPI en Windows
REM Fuerza el uso del venv de Poetry y evita interferencias con Anaconda

echo ========================================
echo Sistema de Agenda Clinica - Boxes
echo Iniciando servidor FastAPI...
echo ========================================

REM Limpiar PYTHONPATH para evitar conflictos con Anaconda
set PYTHONPATH=

REM Forzar uso del interprete de Poetry en .venv
REM Esto evita que Uvicorn intente usar Anaconda
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir ./app

pause
