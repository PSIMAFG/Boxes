@echo off
REM Script para configurar la base de datos (migraciones + seed)

echo ========================================
echo Sistema de Agenda Clinica - Boxes
echo Configurando Base de Datos...
echo ========================================

REM Limpiar PYTHONPATH para evitar conflictos
set PYTHONPATH=

echo.
echo [1/2] Ejecutando migraciones de Alembic...
poetry run alembic upgrade head

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Las migraciones fallaron
    pause
    exit /b 1
)

echo.
echo [2/2] Poblando base de datos con datos iniciales...
poetry run python -m app.scripts.seed_data

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: El seed de datos fallo
    pause
    exit /b 1
)

echo.
echo ========================================
echo ^✓ Base de datos configurada exitosamente
echo ========================================
echo.
echo Credenciales de acceso:
echo.
echo Admin:
echo   Email: admin@clinica.cl
echo   Password: admin123
echo.
echo Recepcion:
echo   Email: recepcion@clinica.cl
echo   Password: recepcion123
echo.
echo Profesional:
echo   Email: juan.perez@clinica.cl
echo   Password: prof123
echo.
pause
