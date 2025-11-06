"""
Reglas de negocio y validadores del dominio.
No tienen dependencias con capas externas.
"""
import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

RUT_RE = re.compile(r'^\d{7,8}-[0-9K]$')


def validar_rut(rut: str) -> bool:
    """
    Valida RUT chileno con módulo 11.

    Args:
        rut: RUT en formato "12345678-5" o "7654321-K"

    Returns:
        True si el RUT es válido, False en caso contrario

    Examples:
        >>> validar_rut("12345678-5")
        True
        >>> validar_rut("12345678-9")
        False
        >>> validar_rut("7654321-K")
        True
    """
    rut = rut.strip().upper()
    if not RUT_RE.match(rut):
        return False

    cuerpo, dv = rut.split('-')
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_calculado = '0'
    elif resto == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(resto)

    return dv_calculado == dv


def validar_solapamiento(
    inicio1: datetime,
    fin1: datetime,
    inicio2: datetime,
    fin2: datetime
) -> bool:
    """
    Retorna True si los rangos temporales se solapan.

    Args:
        inicio1: Inicio del primer rango
        fin1: Fin del primer rango
        inicio2: Inicio del segundo rango
        fin2: Fin del segundo rango

    Returns:
        True si hay solapamiento, False si no

    Examples:
        # No solapan (consecutivos)
        >>> validar_solapamiento(
        ...     datetime(2025, 1, 1, 10, 0),
        ...     datetime(2025, 1, 1, 11, 0),
        ...     datetime(2025, 1, 1, 11, 0),
        ...     datetime(2025, 1, 1, 12, 0)
        ... )
        False

        # Solapan parcialmente
        >>> validar_solapamiento(
        ...     datetime(2025, 1, 1, 10, 0),
        ...     datetime(2025, 1, 1, 11, 30),
        ...     datetime(2025, 1, 1, 11, 0),
        ...     datetime(2025, 1, 1, 12, 0)
        ... )
        True
    """
    return not (fin1 <= inicio2 or fin2 <= inicio1)


def validar_periodicidad(periodicidad_dias: int, tolerancia_dias: int) -> bool:
    """
    Valida que periodicidad > 0 y tolerancia >= 0.

    Args:
        periodicidad_dias: Días entre citas
        tolerancia_dias: Días de tolerancia permitidos

    Returns:
        True si los valores son válidos
    """
    return periodicidad_dias > 0 and tolerancia_dias >= 0


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto: strip, lowercase, elimina acentos, múltiples espacios.

    Args:
        texto: Texto a normalizar

    Returns:
        Texto normalizado

    Examples:
        >>> normalizar_texto("  José  María  ")
        'jose maria'
        >>> normalizar_texto("ÑOÑO")
        'nono'
    """
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def calcular_fecha_objetivo_proxima(
    ultima_cita: Optional[datetime],
    periodicidad_dias: int
) -> datetime:
    """
    Calcula fecha objetivo para próxima cita basado en periodicidad.
    Si no hay última cita, retorna fecha actual.

    Args:
        ultima_cita: Fecha de la última cita cumplida (o None)
        periodicidad_dias: Días de periodicidad

    Returns:
        Fecha objetivo para próxima cita
    """
    if ultima_cita is None:
        return datetime.utcnow()
    return ultima_cita + timedelta(days=periodicidad_dias)


def esta_en_ventana_tolerancia(
    fecha: datetime,
    fecha_objetivo: datetime,
    tolerancia_dias: int
) -> bool:
    """
    Verifica si fecha está dentro de ventana de tolerancia.

    Ventana: [fecha_objetivo - tolerancia, fecha_objetivo + tolerancia]

    Args:
        fecha: Fecha a verificar
        fecha_objetivo: Fecha objetivo ideal
        tolerancia_dias: Días de tolerancia a ambos lados

    Returns:
        True si está dentro de la ventana
    """
    delta_dias = abs((fecha.date() - fecha_objetivo.date()).days)
    return delta_dias <= tolerancia_dias


def validar_edad_minima(fecha_nacimiento: datetime, edad_minima: int = 0) -> bool:
    """
    Valida que una persona tenga edad mínima requerida.

    Args:
        fecha_nacimiento: Fecha de nacimiento
        edad_minima: Edad mínima requerida (default 0)

    Returns:
        True si cumple con edad mínima
    """
    from datetime import date
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return edad >= edad_minima
