#!/usr/bin/env python3
"""
Script para generar una clave de cifrado Fernet
Ejecutar y copiar la salida al archivo .env en la variable ENCRYPTION_KEY
"""

from cryptography.fernet import Fernet

def generate_encryption_key():
    """Genera y muestra una clave de cifrado Fernet"""
    key = Fernet.generate_key()
    key_str = key.decode()

    print("=" * 60)
    print("🔐 CLAVE DE CIFRADO GENERADA")
    print("=" * 60)
    print()
    print(key_str)
    print()
    print("=" * 60)
    print("📋 Copiar esta clave al archivo .env")
    print("   Variable: ENCRYPTION_KEY")
    print("=" * 60)
    print()
    print("Ejemplo en .env:")
    print(f"ENCRYPTION_KEY={key_str}")
    print()

if __name__ == "__main__":
    generate_encryption_key()
