# Código Base - Componentes Principales

## dominio/entidades.py

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID, uuid4
from .valores import RUT, Periodicidad

@dataclass
class Usuario:
    """
    Usuario del sistema clínico (paciente/beneficiario).
    Invariantes:
    - RUT debe ser válido según módulo 11
    - Nombre mínimo 3 caracteres
    - Nivel de apoyo entre 1-3 o None
    """
    id: UUID = field(default_factory=uuid4)
    rut: RUT
    nombre: str
    fecha_nacimiento: date
    nivel_apoyo: Optional[Literal[1, 2, 3]] = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.rut.es_valido():
            raise ValueError(f"RUT inválido: {self.rut.valor}")
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise ValueError("Nombre debe tener al menos 3 caracteres")

    def edad(self) -> int:
        """Calcula edad actual en años"""
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def requiere_apoyo_especial(self) -> bool:
        """Indica si usuario requiere nivel de apoyo 2 o 3"""
        return self.nivel_apoyo in [2, 3]


@dataclass
class Profesional:
    """Terapeuta o médico que realiza prestaciones"""
    id: UUID = field(default_factory=uuid4)
    nombre: str
    profesion: str
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise ValueError("Nombre debe tener al menos 3 caracteres")
        if not self.profesion or len(self.profesion.strip()) < 3:
            raise ValueError("Profesión debe tener al menos 3 caracteres")


@dataclass
class Box:
    """Sala o consultorio físico"""
    id: UUID = field(default_factory=uuid4)
    nombre: str
    ubicacion: str
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError("Nombre de box debe tener al menos 2 caracteres")


@dataclass
class Prestacion:
    """
    Tipo de servicio clínico.
    Incluye periodicidad para control de tratamientos recurrentes.
    """
    id: UUID = field(default_factory=uuid4)
    nombre: str
    duracion_minutos: int
    periodicidad_dias: int
    tolerancia_dias: int
    habilitada: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.duracion_minutos <= 0 or self.duracion_minutos > 480:
            raise ValueError("Duración debe estar entre 1 y 480 minutos")
        if self.periodicidad_dias <= 0:
            raise ValueError("Periodicidad debe ser mayor a 0 días")
        if self.tolerancia_dias < 0:
            raise ValueError("Tolerancia no puede ser negativa")

    def periodicidad(self) -> Periodicidad:
        """Retorna value object de periodicidad"""
        return Periodicidad(
            periodicidad_dias=self.periodicidad_dias,
            tolerancia_dias=self.tolerancia_dias
        )

    def es_recurrente(self) -> bool:
        """Indica si la prestación requiere seguimiento periódico"""
        return self.periodicidad_dias > 0


@dataclass
class Cita:
    """
    Agendamiento de una sesión clínica.
    Invariantes:
    - fin debe ser posterior a inicio
    - inicio no puede ser en el pasado
    - estado debe ser válido
    """
    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID
    profesional_id: UUID
    prestacion_id: UUID
    box_id: UUID
    inicio: datetime
    fin: datetime
    estado: Literal["programada", "confirmada", "cumplida", "no_asistio", "cancelada"] = "programada"
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("inicio debe ser anterior a fin")
        if self.inicio < datetime.utcnow():
            raise ValueError("No se puede crear cita en el pasado")

    def duracion_minutos(self) -> int:
        """Retorna duración de la cita en minutos"""
        return int((self.fin - self.inicio).total_seconds() / 60)

    def esta_pendiente(self) -> bool:
        """Indica si cita está programada o confirmada"""
        return self.estado in ["programada", "confirmada"]

    def fue_cumplida(self) -> bool:
        """Indica si cita fue realizada exitosamente"""
        return self.estado == "cumplida"

    def puede_registrarse(self) -> bool:
        """Indica si se puede registrar resultado de sesión"""
        return self.estado in ["programada", "confirmada"]


@dataclass
class SesionRegistro:
    """Registro de resultado de una cita realizada"""
    id: UUID = field(default_factory=uuid4)
    cita_id: UUID
    cumplida: bool
    valoracion: Optional[Literal["positivo", "neutro", "negativo"]] = None
    notas: Optional[str] = None
    creado_por: UUID
    creado_en: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alerta:
    """
    Notificación de usuario fuera de control.
    Nivel info: preventivo (7 días antes)
    Nivel warn: en ventana sin cita programada
    Nivel crit: fuera de ventana de tolerancia
    """
    id: UUID = field(default_factory=uuid4)
    usuario_id: UUID
    prestacion_id: UUID
    nivel: Literal["info", "warn", "crit"]
    motivo: str
    fecha_objetivo: date
    resuelta: bool = False
    creado_en: datetime = field(default_factory=datetime.utcnow)
    resuelta_en: Optional[datetime] = None

    def es_critica(self) -> bool:
        """Indica si alerta es crítica y requiere acción inmediata"""
        return self.nivel == "crit"
```

---

## dominio/valores.py

```python
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
```

---

## dominio/reglas.py

```python
import re
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

RUT_RE = re.compile(r'^\d{7,8}-[0-9K]$')

def validar_rut(rut: str) -> bool:
    """
    Valida RUT chileno con módulo 11.
    
    Ejemplos:
        validar_rut("12345678-5") -> True
        validar_rut("12345678-9") -> False
        validar_rut("7654321-K") -> True
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
    Retorna True si los rangos se solapan.
    
    Ejemplos:
        # No solapan
        validar_solapamiento(
            datetime(2025, 1, 1, 10, 0),
            datetime(2025, 1, 1, 11, 0),
            datetime(2025, 1, 1, 11, 0),
            datetime(2025, 1, 1, 12, 0)
        ) -> False
        
        # Solapan parcialmente
        validar_solapamiento(
            datetime(2025, 1, 1, 10, 0),
            datetime(2025, 1, 1, 11, 30),
            datetime(2025, 1, 1, 11, 0),
            datetime(2025, 1, 1, 12, 0)
        ) -> True
    """
    return not (fin1 <= inicio2 or fin2 <= inicio1)


def validar_periodicidad(periodicidad_dias: int, tolerancia_dias: int) -> bool:
    """
    Valida que periodicidad > 0 y tolerancia >= 0.
    """
    return periodicidad_dias > 0 and tolerancia_dias >= 0


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto: strip, lowercase, elimina acentos, múltiples espacios.
    
    Ejemplos:
        normalizar_texto("  José  María  ") -> "jose maria"
        normalizar_texto("ÑOÑO") -> "nono"
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
    """
    delta_dias = abs((fecha.date() - fecha_objetivo.date()).days)
    return delta_dias <= tolerancia_dias
```

---

## dominio/repositorios.py

```python
from typing import Protocol, Optional
from datetime import datetime
from uuid import UUID
from .entidades import Usuario, Cita, Profesional, Prestacion, Alerta, SesionRegistro
from .valores import RUT, RangoTiempo
from typing import Literal

class IUsuarioRepo(Protocol):
    """Interfaz de repositorio para Usuario"""
    
    def obtener_por_rut(self, rut: RUT) -> Optional[Usuario]:
        """Busca usuario por RUT"""
        ...
    
    def obtener(self, id: UUID) -> Optional[Usuario]:
        """Obtiene usuario por ID"""
        ...
    
    def crear(self, usuario: Usuario) -> Usuario:
        """Crea nuevo usuario"""
        ...
    
    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza usuario existente"""
        ...
    
    def listar(self, activo: Optional[bool] = None) -> list[Usuario]:
        """Lista usuarios con filtro opcional de activo"""
        ...


class IAgendaRepo(Protocol):
    """Interfaz de repositorio para Agenda (Citas y Bloqueos)"""
    
    def buscar_citas(
        self,
        profesional_id: Optional[UUID],
        box_id: Optional[UUID],
        rango: RangoTiempo
    ) -> list[Cita]:
        """Busca citas con filtros opcionales"""
        ...
    
    def crear_cita(self, cita: Cita) -> Cita:
        """Crea nueva cita"""
        ...
    
    def obtener(self, cita_id: UUID) -> Optional[Cita]:
        """Obtiene cita por ID"""
        ...
    
    def actualizar_estado(self, cita_id: UUID, estado: str) -> None:
        """Actualiza estado de una cita"""
        ...
    
    def hay_solape(
        self,
        profesional_id: UUID,
        box_id: UUID,
        inicio: datetime,
        fin: datetime,
        excluir_cita_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica si existe solape temporal para profesional y box.
        Puede excluir una cita específica (útil para modificaciones).
        """
        ...
    
    def obtener_ultima_cita_usuario_prestacion(
        self,
        usuario_id: UUID,
        prestacion_id: UUID
    ) -> Optional[Cita]:
        """Obtiene última cita cumplida de usuario para prestación específica"""
        ...


class ISesionesRepo(Protocol):
    """Interfaz de repositorio para Sesiones"""
    
    def crear_registro(self, sesion: SesionRegistro) -> SesionRegistro:
        """Crea nuevo registro de sesión"""
        ...
    
    def obtener_por_cita(self, cita_id: UUID) -> Optional[SesionRegistro]:
        """Obtiene registro de sesión por ID de cita"""
        ...


class IAlertasRepo(Protocol):
    """Interfaz de repositorio para Alertas"""
    
    def crear(self, alerta: Alerta) -> Alerta:
        """Crea nueva alerta"""
        ...
    
    def listar_pendientes(
        self,
        usuario_id: Optional[UUID] = None,
        nivel: Optional[str] = None
    ) -> list[Alerta]:
        """Lista alertas no resueltas con filtros opcionales"""
        ...
    
    def marcar_resuelta(self, alerta_id: UUID) -> None:
        """Marca alerta como resuelta"""
        ...
```

---

## Tests Ejemplo

### tests/unit/test_reglas.py

```python
import pytest
from datetime import datetime, timedelta
from app.dominio.reglas import (
    validar_rut, validar_solapamiento, normalizar_texto,
    esta_en_ventana_tolerancia
)


class TestValidarRUT:
    def test_rut_valido_con_digito(self):
        assert validar_rut("12345678-5") == True
    
    def test_rut_valido_con_k(self):
        assert validar_rut("7654321-K") == True
    
    def test_rut_invalido_dv_incorrecto(self):
        assert validar_rut("12345678-9") == False
    
    def test_rut_formato_invalido(self):
        assert validar_rut("1234567") == False
    
    def test_rut_con_espacios(self):
        assert validar_rut("  12345678-5  ") == True


class TestValidarSolapamiento:
    def test_no_solape_consecutivos(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 11, 0)
        inicio2 = datetime(2025, 1, 1, 11, 0)
        fin2 = datetime(2025, 1, 1, 12, 0)
        
        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == False
    
    def test_solape_parcial(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 11, 30)
        inicio2 = datetime(2025, 1, 1, 11, 0)
        fin2 = datetime(2025, 1, 1, 12, 0)
        
        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == True
    
    def test_solape_completo(self):
        inicio1 = datetime(2025, 1, 1, 10, 0)
        fin1 = datetime(2025, 1, 1, 12, 0)
        inicio2 = datetime(2025, 1, 1, 10, 30)
        fin2 = datetime(2025, 1, 1, 11, 30)
        
        assert validar_solapamiento(inicio1, fin1, inicio2, fin2) == True


class TestNormalizarTexto:
    def test_con_acentos(self):
        assert normalizar_texto("José María") == "jose maria"
    
    def test_con_enies(self):
        assert normalizar_texto("ÑOÑO") == "nono"
    
    def test_con_espacios_multiples(self):
        assert normalizar_texto("  hola   mundo  ") == "hola mundo"
    
    def test_mayusculas(self):
        assert normalizar_texto("TEXTO MAYÚSCULAS") == "texto mayusculas"


class TestVentanaTolerancia:
    def test_dentro_de_ventana(self):
        fecha = datetime(2025, 1, 15)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7
        
        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == True
    
    def test_fuera_de_ventana(self):
        fecha = datetime(2025, 1, 20)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7
        
        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == False
    
    def test_exactamente_en_limite(self):
        fecha = datetime(2025, 1, 17)
        fecha_objetivo = datetime(2025, 1, 10)
        tolerancia = 7
        
        assert esta_en_ventana_tolerancia(fecha, fecha_objetivo, tolerancia) == True
```

### tests/unit/test_entidades.py

```python
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from app.dominio.entidades import Usuario, Cita, Prestacion
from app.dominio.valores import RUT


class TestUsuario:
    def test_crear_usuario_valido(self):
        usuario = Usuario(
            rut=RUT("12345678-5"),
            nombre="Juan Pérez",
            fecha_nacimiento=date(1980, 1, 1),
            nivel_apoyo=2
        )
        
        assert usuario.nombre == "Juan Pérez"
        assert usuario.nivel_apoyo == 2
    
    def test_rut_invalido_lanza_error(self):
        with pytest.raises(ValueError, match="RUT inválido"):
            Usuario(
                rut=RUT("12345678-9"),  # DV incorrecto
                nombre="Juan Pérez",
                fecha_nacimiento=date(1980, 1, 1)
            )
    
    def test_nombre_muy_corto_lanza_error(self):
        with pytest.raises(ValueError, match="al menos 3 caracteres"):
            Usuario(
                rut=RUT("12345678-5"),
                nombre="AB",
                fecha_nacimiento=date(1980, 1, 1)
            )
    
    def test_calculo_edad(self):
        usuario = Usuario(
            rut=RUT("12345678-5"),
            nombre="Juan Pérez",
            fecha_nacimiento=date(1980, 1, 1)
        )
        
        edad = usuario.edad()
        assert edad >= 44  # Depende del año actual
    
    def test_requiere_apoyo_especial(self):
        usuario_nivel_3 = Usuario(
            rut=RUT("12345678-5"),
            nombre="Juan Pérez",
            fecha_nacimiento=date(1980, 1, 1),
            nivel_apoyo=3
        )
        
        assert usuario_nivel_3.requiere_apoyo_especial() == True
        
        usuario_nivel_1 = Usuario(
            rut=RUT("98765432-1"),
            nombre="María González",
            fecha_nacimiento=date(1975, 5, 15),
            nivel_apoyo=1
        )
        
        assert usuario_nivel_1.requiere_apoyo_especial() == False


class TestCita:
    def test_crear_cita_valida(self):
        ahora = datetime.utcnow()
        cita = Cita(
            usuario_id=uuid4(),
            profesional_id=uuid4(),
            prestacion_id=uuid4(),
            box_id=uuid4(),
            inicio=ahora + timedelta(hours=1),
            fin=ahora + timedelta(hours=2)
        )
        
        assert cita.duracion_minutos() == 60
        assert cita.estado == "programada"
    
    def test_fin_antes_de_inicio_lanza_error(self):
        ahora = datetime.utcnow()
        with pytest.raises(ValueError, match="anterior a fin"):
            Cita(
                usuario_id=uuid4(),
                profesional_id=uuid4(),
                prestacion_id=uuid4(),
                box_id=uuid4(),
                inicio=ahora + timedelta(hours=2),
                fin=ahora + timedelta(hours=1)
            )
    
    def test_cita_en_pasado_lanza_error(self):
        with pytest.raises(ValueError, match="en el pasado"):
            Cita(
                usuario_id=uuid4(),
                profesional_id=uuid4(),
                prestacion_id=uuid4(),
                box_id=uuid4(),
                inicio=datetime(2020, 1, 1, 10, 0),
                fin=datetime(2020, 1, 1, 11, 0)
            )


class TestPrestacion:
    def test_crear_prestacion_valida(self):
        prestacion = Prestacion(
            nombre="Kinesiología",
            duracion_minutos=45,
            periodicidad_dias=30,
            tolerancia_dias=7
        )
        
        assert prestacion.nombre == "Kinesiología"
        assert prestacion.es_recurrente() == True
    
    def test_duracion_invalida_lanza_error(self):
        with pytest.raises(ValueError, match="entre 1 y 480"):
            Prestacion(
                nombre="Kinesiología",
                duracion_minutos=0,
                periodicidad_dias=30,
                tolerancia_dias=7
            )
    
    def test_periodicidad_invalida_lanza_error(self):
        with pytest.raises(ValueError, match="mayor a 0"):
            Prestacion(
                nombre="Kinesiología",
                duracion_minutos=45,
                periodicidad_dias=0,
                tolerancia_dias=7
            )
```

---

## Uso del Código

### Crear Usuario

```python
from app.dominio.entidades import Usuario
from app.dominio.valores import RUT
from datetime import date

try:
    usuario = Usuario(
        rut=RUT("12345678-5"),
        nombre="Juan Pérez González",
        fecha_nacimiento=date(1980, 5, 15),
        nivel_apoyo=2
    )
    print(f"Usuario creado: {usuario.nombre}, edad: {usuario.edad()} años")
except ValueError as e:
    print(f"Error: {e}")
```

### Validar Cita Sin Solapes

```python
from app.dominio.reglas import validar_solapamiento
from datetime import datetime

inicio_cita_existente = datetime(2025, 1, 15, 10, 0)
fin_cita_existente = datetime(2025, 1, 15, 11, 0)

inicio_nueva_cita = datetime(2025, 1, 15, 10, 30)
fin_nueva_cita = datetime(2025, 1, 15, 11, 30)

if validar_solapamiento(
    inicio_cita_existente, fin_cita_existente,
    inicio_nueva_cita, fin_nueva_cita
):
    print("Error: Las citas se solapan")
else:
    print("OK: No hay solape")
```

### Ejecutar Tests

```bash
pytest tests/unit/test_reglas.py -v
pytest tests/unit/test_entidades.py -v
pytest tests/ --cov=app --cov-report=html
```
