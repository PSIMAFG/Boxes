#!/usr/bin/env python3
"""
Script para verificar que el entorno está correctamente configurado
"""

import sys
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 o superior es requerido")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required = [
        ("PyQt6", "PyQt6"),
        ("qasync", "qasync"),
        ("httpx", "httpx"),
        ("dotenv", "python-dotenv"),
        ("cryptography", "cryptography"),
        ("pydantic", "pydantic"),
    ]

    all_ok = True
    for module_name, package_name in required:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - No instalado")
            all_ok = False

    return all_ok

def check_env_file():
    """Verifica que exista el archivo .env"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print("✅ Archivo .env encontrado")

        # Verificar contenido básico
        content = env_path.read_text()
        if "API_BASE_URL" in content and "ENCRYPTION_KEY" in content:
            print("✅ Variables de entorno configuradas")
            return True
        else:
            print("⚠️  Archivo .env incompleto")
            print("   Verificar que contenga API_BASE_URL y ENCRYPTION_KEY")
            return False
    else:
        print("❌ Archivo .env no encontrado")
        print("   Copiar .env.example a .env y configurar")
        return False

def check_structure():
    """Verifica la estructura de carpetas"""
    base_path = Path(__file__).parent.parent
    required_dirs = [
        "controllers",
        "ui",
        "resources",
    ]

    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ Directorio {dir_name}/")
        else:
            print(f"❌ Directorio {dir_name}/ no encontrado")
            all_ok = False

    # Verificar main.py
    main_path = base_path / "main.py"
    if main_path.exists():
        print("✅ main.py")
    else:
        print("❌ main.py no encontrado")
        all_ok = False

    return all_ok

def main():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    print("   Sistema de Agenda Clínica - Frontend PyQt6")
    print("=" * 60)
    print()

    print("📦 Verificando Python:")
    python_ok = check_python_version()
    print()

    print("📦 Verificando dependencias:")
    deps_ok = check_dependencies()
    print()

    print("⚙️  Verificando configuración:")
    env_ok = check_env_file()
    print()

    print("📁 Verificando estructura:")
    structure_ok = check_structure()
    print()

    print("=" * 60)
    if all([python_ok, deps_ok, env_ok, structure_ok]):
        print("✅ TODO LISTO - Puedes ejecutar: python main.py")
    else:
        print("❌ HAY PROBLEMAS - Revisar los items marcados con ❌")
        print()
        print("💡 Pasos sugeridos:")
        if not deps_ok:
            print("   1. pip install -r requirements.txt")
        if not env_ok:
            print("   2. cp .env.example .env")
            print("   3. Configurar .env con tus valores")
    print("=" * 60)

if __name__ == "__main__":
    main()
