@echo off
REM Script para ejecutar Backend + Frontend en paralelo

echo ========================================
echo Sistema de Agenda Clinica
echo Iniciando Backend y Frontend...
echo ========================================

REM Verificar que poetry esta instalado (para backend)
where poetry >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Poetry no esta instalado
    echo.
    echo El backend requiere Poetry. Instalar desde:
    echo https://python-poetry.org/docs/#installation
    echo.
    echo O ejecuta solo el frontend con:
    echo   cd frontend_pyqt
    echo   run_frontend.bat
    pause
    exit /b 1
)

echo.
echo [1/2] Iniciando Backend FastAPI en puerto 8000...
echo.

REM Iniciar backend en background
start "Backend FastAPI" cmd /k "run_server.bat"

REM Esperar 5 segundos para que el backend inicie
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Iniciando Frontend PyQt6...
echo.

REM Cambiar a directorio del frontend
cd frontend_pyqt

REM Verificar que el venv existe
if not exist venv\ (
    echo.
    echo ADVERTENCIA: No se encuentra el entorno virtual del frontend
    echo.
    echo Configurando frontend por primera vez...
    echo.

    REM Crear venv
    python -m venv venv

    REM Activar e instalar dependencias
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt

    REM Copiar .env si no existe
    if not exist .env (
        copy .env.example .env
        echo.
        echo Por favor configura .env con ENCRYPTION_KEY
        echo Ejecuta: python scripts\generate_key.py
        echo.
        pause
    )
)

REM Ejecutar frontend
call run_frontend.bat

REM Si el frontend se cierra, preguntar si detener backend
echo.
echo Frontend cerrado.
echo.
choice /C SN /M "¿Detener tambien el backend?"
if errorlevel 2 (
    echo Backend sigue corriendo en segundo plano
) else (
    taskkill /FI "WindowTitle eq Backend FastAPI*" /T /F >nul 2>&1
    echo Backend detenido
)
