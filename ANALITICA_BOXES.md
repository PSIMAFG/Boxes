# Analítica y Simulación de Uso de Boxes

Este documento describe la funcionalidad de análisis y simulación del uso dinámico de boxes (consultorios/salas).

## Descripción General

El sistema de analítica permite:
- Visualizar el uso de boxes hora a hora, día a día, y semana a semana
- Calcular porcentajes de ocupación en diferentes períodos
- Comparar el rendimiento entre múltiples boxes
- Analizar el uso por piso (Piso 1 y Piso 2)
- Mantener un historial de cambios de características de los boxes
- Modificar características de boxes en el tiempo (piso, capacidad, equipamiento)

## Características de Boxes

Cada box ahora tiene las siguientes características configurables:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | String | Nombre identificador del box |
| `ubicacion` | String | Ubicación física detallada |
| `piso` | Integer (1 o 2) | Piso donde se encuentra el box |
| `capacidad` | Integer | Número de personas que puede atender simultáneamente |
| `equipamiento` | String | Descripción del equipamiento disponible |
| `metros_cuadrados` | Float | Tamaño del box en metros cuadrados |
| `activo` | Boolean | Si el box está activo y disponible |

## Endpoints Disponibles

Todos los endpoints están bajo el prefijo `/api/v1/analitica/` y requieren autenticación.

### 1. Uso Horario

```http
GET /api/v1/analitica/boxes/{box_id}/uso-horario?fecha=2025-01-15
```

**Respuesta:**
```json
[
  {
    "hora": 10,
    "minutos_ocupados": 45,
    "minutos_disponibles": 60,
    "porcentaje_uso": 75.0,
    "numero_citas": 1
  },
  ...
]
```

Muestra el uso del box hora por hora (0-23) en un día específico.

### 2. Uso Diario

```http
GET /api/v1/analitica/boxes/{box_id}/uso-diario?fecha=2025-01-15&incluir_horas=true
```

**Respuesta:**
```json
{
  "fecha": "2025-01-15",
  "dia_semana": "Miércoles",
  "minutos_ocupados": 360,
  "minutos_disponibles": 540,
  "porcentaje_uso": 66.67,
  "numero_citas": 8,
  "uso_por_hora": [...]
}
```

Muestra el uso total del box en un día. Opcionalmente incluye el detalle hora por hora.

### 3. Uso Semanal

```http
GET /api/v1/analitica/boxes/{box_id}/uso-semanal?fecha=2025-01-15&incluir_dias=true
```

**Respuesta:**
```json
{
  "semana": 3,
  "año": 2025,
  "fecha_inicio": "2025-01-13",
  "fecha_fin": "2025-01-19",
  "minutos_ocupados": 1800,
  "minutos_disponibles": 2700,
  "porcentaje_uso": 66.67,
  "numero_citas": 40,
  "uso_por_dia": [...]
}
```

Muestra el uso del box en una semana completa (lunes a domingo). Opcionalmente incluye el detalle día por día.

### 4. Estadísticas de Box

```http
GET /api/v1/analitica/boxes/{box_id}/estadisticas?fecha_inicio=2025-01-01T00:00:00&fecha_fin=2025-01-31T23:59:59
```

**Respuesta:**
```json
{
  "box_id": "123e4567-e89b-12d3-a456-426614174000",
  "box_nombre": "Box 1",
  "piso": 1,
  "capacidad": 1,
  "periodo_inicio": "2025-01-01T00:00:00",
  "periodo_fin": "2025-01-31T23:59:59",
  "total_minutos_ocupados": 7200,
  "total_minutos_disponibles": 10800,
  "porcentaje_uso_promedio": 66.67,
  "total_citas": 160,
  "uso_piso": 70.5
}
```

Muestra estadísticas completas de un box en un período personalizado.

### 5. Comparativa de Boxes

```http
GET /api/v1/analitica/boxes/comparativa?fecha_inicio=2025-01-01T00:00:00&fecha_fin=2025-01-31T23:59:59&piso=1
```

**Parámetros de consulta:**
- `fecha_inicio` (requerido): Inicio del período
- `fecha_fin` (requerido): Fin del período
- `box_ids` (opcional): IDs separados por comas (ej: "uuid1,uuid2")
- `piso` (opcional): Filtrar por piso (1 o 2)
- `incluir_inactivos` (opcional): Incluir boxes inactivos (default: false)

**Respuesta:**
```json
{
  "periodo_inicio": "2025-01-01T00:00:00",
  "periodo_fin": "2025-01-31T23:59:59",
  "estadisticas_boxes": [...],
  "porcentaje_uso_piso_1": 65.3,
  "porcentaje_uso_piso_2": 58.7,
  "box_mayor_uso": {...},
  "box_menor_uso": {...}
}
```

Compara el uso de múltiples boxes mostrando:
- Estadísticas individuales de cada box
- Promedio de uso por piso
- Box con mayor y menor ocupación

### 6. Historial de Cambios

```http
GET /api/v1/analitica/boxes/{box_id}/historial?fecha_inicio=2025-01-01T00:00:00
```

**Respuesta:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "box_id": "123e4567-e89b-12d3-a456-426614174001",
    "campo_modificado": "piso",
    "valor_anterior": "1",
    "valor_nuevo": "2",
    "motivo": "Reasignación por obras en piso 1",
    "modificado_por": "123e4567-e89b-12d3-a456-426614174002",
    "timestamp": "2025-01-15T10:30:00"
  }
]
```

Muestra todos los cambios realizados en las características del box.

### 7. Actualizar Características (Solo Admin)

```http
PATCH /api/v1/analitica/boxes/{box_id}/caracteristicas
```

**Body:**
```json
{
  "piso": 2,
  "capacidad": 2,
  "equipamiento": "Camilla eléctrica, ultrasonido",
  "metros_cuadrados": 15.5,
  "ubicacion": "Piso 2, Ala Norte",
  "activo": true,
  "motivo_cambio": "Ampliación de instalaciones"
}
```

**Respuesta:**
```json
{
  "mensaje": "Box actualizado exitosamente",
  "cambios_realizados": ["piso", "capacidad", "equipamiento"],
  "box": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "nombre": "Box 1",
    "piso": 2,
    "capacidad": 2,
    "equipamiento": "Camilla eléctrica, ultrasonido",
    "metros_cuadrados": 15.5,
    "ubicacion": "Piso 2, Ala Norte",
    "activo": true
  }
}
```

Actualiza las características de un box y registra automáticamente los cambios en el historial.

**Nota:** Solo usuarios con rol `admin` pueden modificar características de boxes.

## Casos de Uso

### 1. Análisis de Ocupación Diaria

Para ver cómo se está usando un box durante un día específico:

```bash
curl -X GET "http://localhost:8000/api/v1/analitica/boxes/{box_id}/uso-diario?fecha=2025-01-15&incluir_horas=true" \
  -H "Authorization: Bearer {token}"
```

Esto muestra:
- El porcentaje de ocupación total del día
- Cuántas citas se atendieron
- El detalle hora por hora del uso

### 2. Comparar Rendimiento entre Pisos

Para comparar cómo se están usando los boxes del Piso 1 vs Piso 2:

```bash
# Piso 1
curl -X GET "http://localhost:8000/api/v1/analitica/boxes/comparativa?fecha_inicio=2025-01-01T00:00:00&fecha_fin=2025-01-31T23:59:59&piso=1" \
  -H "Authorization: Bearer {token}"

# Piso 2
curl -X GET "http://localhost:8000/api/v1/analitica/boxes/comparativa?fecha_inicio=2025-01-01T00:00:00&fecha_fin=2025-01-31T23:59:59&piso=2" \
  -H "Authorization: Bearer {token}"
```

### 3. Identificar Boxes Subutilizados

Use el endpoint de comparativa para ver qué box tiene el menor uso:

```bash
curl -X GET "http://localhost:8000/api/v1/analitica/boxes/comparativa?fecha_inicio=2025-01-01T00:00:00&fecha_fin=2025-01-31T23:59:59" \
  -H "Authorization: Bearer {token}"
```

El campo `box_menor_uso` mostrará el box con menor ocupación.

### 4. Reasignar Box a Otro Piso

Para mover un box del Piso 1 al Piso 2 (requiere permisos de admin):

```bash
curl -X PATCH "http://localhost:8000/api/v1/analitica/boxes/{box_id}/caracteristicas" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "piso": 2,
    "motivo_cambio": "Redistribución de carga entre pisos"
  }'
```

Este cambio queda registrado en el historial del box.

### 5. Análisis de Tendencias Semanales

Para ver cómo varía el uso de un box a lo largo de una semana:

```bash
curl -X GET "http://localhost:8000/api/v1/analitica/boxes/{box_id}/uso-semanal?fecha=2025-01-15&incluir_dias=true" \
  -H "Authorization: Bearer {token}"
```

Esto muestra qué días de la semana tienen mayor demanda.

## Base de Datos

### Cambios en la Tabla `boxes`

Se agregaron los siguientes campos:

```sql
ALTER TABLE boxes ADD COLUMN piso INTEGER NOT NULL DEFAULT 1;
ALTER TABLE boxes ADD COLUMN capacidad INTEGER NOT NULL DEFAULT 1;
ALTER TABLE boxes ADD COLUMN equipamiento TEXT;
ALTER TABLE boxes ADD COLUMN metros_cuadrados INTEGER;
ALTER TABLE boxes ADD CONSTRAINT check_piso CHECK (piso IN (1, 2));
ALTER TABLE boxes ADD CONSTRAINT check_capacidad CHECK (capacidad >= 1);
```

### Nueva Tabla `historial_boxes`

```sql
CREATE TABLE historial_boxes (
    id UUID PRIMARY KEY,
    box_id UUID NOT NULL REFERENCES boxes(id),
    campo_modificado VARCHAR(50) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT NOT NULL,
    motivo TEXT,
    modificado_por UUID NOT NULL REFERENCES usuarios_sistema(id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_historial_boxes_box_id ON historial_boxes(box_id);
CREATE INDEX ix_historial_boxes_timestamp ON historial_boxes(timestamp);
```

## Migración de Base de Datos

Para aplicar los cambios a una base de datos existente:

```bash
# Ejecutar migración
poetry run alembic upgrade head
```

Para revertir los cambios:

```bash
# Revertir a versión anterior
poetry run alembic downgrade -1
```

## Cálculo de Métricas

### Porcentaje de Uso

```
Porcentaje de Uso = (Minutos Ocupados / Minutos Disponibles) × 100
```

**Asunciones:**
- Se considera un horario de atención de 8 horas diarias (480 minutos)
- Los minutos disponibles se calculan como: `días × 8 × 60`

### Uso por Hora

Para cada hora del día (0-23):
1. Se obtienen todas las citas del box en esa fecha
2. Se calcula cuántos minutos de cada cita caen dentro de cada hora
3. Se suma el total de minutos ocupados por hora
4. Se calcula el porcentaje: `(minutos_ocupados / 60) × 100`

### Uso Semanal

Se suman los usos diarios de lunes a domingo de la semana correspondiente.

## Visualización (Frontend - Pendiente)

Esta API está diseñada para ser consumida por un frontend que pueda visualizar:
- Gráficos de barras mostrando uso hora por hora
- Gráficos de línea mostrando tendencias diarias/semanales
- Mapas de calor mostrando ocupación por día de la semana y hora
- Comparativas visuales entre boxes
- Indicadores de piso (Piso 1 vs Piso 2)

## Permisos

| Endpoint | Admin | Profesional | Recepción |
|----------|-------|-------------|-----------|
| Ver uso horario | ✅ | ✅ | ✅ |
| Ver uso diario | ✅ | ✅ | ✅ |
| Ver uso semanal | ✅ | ✅ | ✅ |
| Ver estadísticas | ✅ | ✅ | ✅ |
| Ver comparativa | ✅ | ✅ | ✅ |
| Ver historial | ✅ | ✅ | ✅ |
| Actualizar características | ✅ | ❌ | ❌ |

## Ejemplos de Datos de Seed

El script de seed (`seed_data.py`) crea 3 boxes de ejemplo:

| Box | Piso | Capacidad | Equipamiento | m² |
|-----|------|-----------|--------------|-----|
| Box 1 | 1 | 1 | Camilla básica, estetoscopio | 12.0 |
| Box 2 | 1 | 2 | Camilla eléctrica, ultrasonido, nebulizador | 15.5 |
| Box 3 | 2 | 1 | Camilla básica, equipamiento de terapia ocupacional | 14.0 |

## Próximas Mejoras

- [ ] Dashboard visual con gráficos interactivos
- [ ] Exportación de reportes en PDF/Excel
- [ ] Alertas automáticas de subutilización
- [ ] Predicción de demanda usando ML
- [ ] Recomendaciones de optimización de uso
- [ ] Análisis de patrones de uso por tipo de prestación
