@echo off
REM Script para instalar/actualizar dependencias con Poetry

echo ========================================
echo Sistema de Agenda Clinica - Boxes
echo Instalando dependencias...
echo ========================================

REM Verificar que Poetry esta instalado
where poetry >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Poetry no esta instalado
    echo Por favor instala Poetry desde: https://python-poetry.org/docs/#installation
    pause
    exit /b 1
)

echo.
echo Instalando dependencias del proyecto...
poetry install --no-root

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo ^✓ Dependencias instaladas exitosamente
echo ========================================
echo.
echo Siguiente paso: ejecutar setup_db.bat
pause
