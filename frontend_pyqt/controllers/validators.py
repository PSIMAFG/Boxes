"""
Validadores de campos del formulario
"""
import re
from typing import Tuple


class Validators:
    """Clase con métodos estáticos para validar campos"""

    @staticmethod
    def validate_rut(rut: str) -> Tuple[bool, str]:
        """
        Valida formato y dígito verificador del RUT chileno

        Args:
            rut: RUT en formato XX.XXX.XXX-X o XXXXXXXX-X

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not rut:
            return False, "El RUT es obligatorio"

        # Limpiar formato
        rut_clean = rut.replace(".", "").replace("-", "").upper()

        if len(rut_clean) < 2:
            return False, "RUT demasiado corto"

        # Separar número y dígito verificador
        numero = rut_clean[:-1]
        dv = rut_clean[-1]

        # Validar que el número sea numérico
        if not numero.isdigit():
            return False, "RUT debe contener solo números (excepto DV)"

        # Calcular dígito verificador esperado
        suma = 0
        multiplicador = 2

        for digit in reversed(numero):
            suma += int(digit) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2

        resto = suma % 11
        dv_esperado = "0" if resto == 11 else ("K" if resto == 10 else str(11 - resto))

        if dv != dv_esperado:
            return False, f"Dígito verificador incorrecto. Debería ser {dv_esperado}"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valida formato de email

        Args:
            email: Dirección de email

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not email:
            return False, "El email es obligatorio"

        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False, "Formato de email inválido"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Valida requisitos de contraseña

        Requisitos:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número

        Args:
            password: Contraseña a validar

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not password:
            return False, "La contraseña es obligatoria"

        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una mayúscula"

        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una minúscula"

        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"

        return True, ""

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Valida nombre de usuario

        Requisitos:
        - Mínimo 3 caracteres
        - Solo letras, números, guiones y guiones bajos

        Args:
            username: Nombre de usuario

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not username:
            return False, "El nombre de usuario es obligatorio"

        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"

        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos"

        return True, ""

    @staticmethod
    def validate_required(value: str, field_name: str = "Este campo") -> Tuple[bool, str]:
        """
        Valida que un campo no esté vacío

        Args:
            value: Valor a validar
            field_name: Nombre del campo para el mensaje de error

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not value or not value.strip():
            return False, f"{field_name} es obligatorio"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valida número de teléfono chileno

        Args:
            phone: Número de teléfono

        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not phone:
            return False, "El teléfono es obligatorio"

        # Limpiar formato
        phone_clean = re.sub(r'[^\d+]', '', phone)

        # Validar longitud (9 dígitos o +569...)
        if phone_clean.startswith('+56'):
            if len(phone_clean) != 12:  # +56 + 9 dígitos
                return False, "Teléfono debe tener 9 dígitos después de +56"
        elif len(phone_clean) != 9:
            return False, "Teléfono debe tener 9 dígitos"

        return True, ""

    @staticmethod
    def format_rut(rut: str) -> str:
        """
        Formatea RUT al formato XX.XXX.XXX-X

        Args:
            rut: RUT sin formato

        Returns:
            RUT formateado
        """
        # Limpiar
        rut_clean = rut.replace(".", "").replace("-", "").upper()

        if len(rut_clean) < 2:
            return rut

        # Separar número y DV
        numero = rut_clean[:-1]
        dv = rut_clean[-1]

        # Formatear con puntos
        formatted = ""
        for i, digit in enumerate(reversed(numero)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted

        return f"{formatted}-{dv}"
