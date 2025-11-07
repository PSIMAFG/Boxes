@echo off
REM Script para ejecutar el Frontend PyQt6 en Windows
REM Asegura que el venv del frontend esté activado

echo ========================================
echo Sistema de Agenda Clinica - Frontend PyQt6
echo ========================================

REM Verificar que estamos en el directorio correcto
if not exist main.py (
    echo ERROR: No se encuentra main.py
    echo Asegurate de ejecutar este script desde: frontend_pyqt\
    pause
    exit /b 1
)

REM Verificar que el venv existe
if not exist venv\ (
    echo ERROR: No se encuentra el entorno virtual
    echo.
    echo Por favor ejecuta primero:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verificar que .env existe
if not exist .env (
    echo ADVERTENCIA: No se encuentra el archivo .env
    echo.
    echo Creando .env desde .env.example...
    copy .env.example .env
    echo.
    echo Por favor configura el archivo .env con:
    echo   1. API_BASE_URL (default: http://localhost:8000)
    echo   2. ENCRYPTION_KEY (ejecuta: python scripts\generate_key.py)
    echo.
    pause
)

echo.
echo Iniciando Frontend PyQt6...
echo.
echo Asegurate de que el backend este corriendo en %API_BASE_URL%
echo (ejecuta run_server.bat en el directorio raiz)
echo.

REM Ejecutar con el Python del venv
venv\Scripts\python.exe main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: El frontend termino con errores
    pause
    exit /b 1
)
