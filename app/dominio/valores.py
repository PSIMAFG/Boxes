"""
Value Objects del dominio.
Objetos inmutables que representan conceptos sin identidad.
"""
from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class RUT:
    """
    Value object para RUT chileno.
    Inmutable, valida formato y dígito verificador.
    """
    valor: str

    def es_valido(self) -> bool:
        """Valida RUT usando algoritmo módulo 11"""
        from .reglas import validar_rut
        return validar_rut(self.valor)

    def __str__(self) -> str:
        return self.valor

    def __post_init__(self):
        if not self.es_valido():
            raise ValueError(f"RUT inválido: {self.valor}")


@dataclass(frozen=True)
class Periodicidad:
    """
    Value object para periodicidad de prestaciones.
    Define intervalo entre citas y tolerancia aceptable.
    """
    periodicidad_dias: int
    tolerancia_dias: int

    def __post_init__(self):
        if self.periodicidad_dias <= 0:
            raise ValueError("periodicidad_dias debe ser > 0")
        if self.tolerancia_dias < 0:
            raise ValueError("tolerancia_dias no puede ser negativo")

    def dias_total_ventana(self) -> int:
        """Retorna ancho total de ventana de tolerancia"""
        return self.tolerancia_dias * 2


@dataclass(frozen=True)
class RangoTiempo:
    """Value object para rango temporal"""
    inicio: datetime
    fin: datetime

    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("inicio debe ser < fin")

    def contiene(self, inicio: datetime, fin: datetime) -> bool:
        """Verifica si otro rango está contenido en este"""
        return self.inicio <= inicio and fin <= self.fin

    def solapa_con(self, otro: 'RangoTiempo') -> bool:
        """Verifica si hay solapamiento con otro rango"""
        return not (self.fin <= otro.inicio or otro.fin <= self.inicio)

    def duracion_minutos(self) -> int:
        """Retorna duración del rango en minutos"""
        return int((self.fin - self.inicio).total_seconds() / 60)


@dataclass(frozen=True)
class Email:
    """Value object para email"""
    valor: str

    def __post_init__(self):
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.valor):
            raise ValueError(f"Email inválido: {self.valor}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class HorarioSemanal:
    """
    Value object para horario semanal.
    Representa un día de la semana con hora de inicio y fin.
    """
    dia_semana: int  # 0=Lunes, 6=Domingo
    hora_inicio: time
    hora_fin: time

    def __post_init__(self):
        if not 0 <= self.dia_semana <= 6:
            raise ValueError("dia_semana debe estar entre 0 (lunes) y 6 (domingo)")
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("hora_inicio debe ser < hora_fin")

    def duracion_minutos(self) -> int:
        """Retorna duración del horario en minutos"""
        delta = datetime.combine(datetime.today(), self.hora_fin) - \
                datetime.combine(datetime.today(), self.hora_inicio)
        return int(delta.total_seconds() / 60)
