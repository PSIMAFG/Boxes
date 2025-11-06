# Sistema de Agenda Clínica con Asignación Dinámica y Analítica ML

## Resumen Ejecutivo

Sistema end-to-end de gestión de agenda clínica que implementa arquitectura limpia con DDD, asignación dinámica de boxes basada en disponibilidad de profesionales y predicciones ML, control de periodicidad de prestaciones, alertas automáticas, RBAC con JWT, auditoría completa y observabilidad.

**Stack tecnológico:**
- Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic V2
- PyQt6 para UI de escritorio
- scikit-learn para modelos predictivos
- PostgreSQL (prod) / SQLite (dev)
- Redis (opcional, caché)

**Características principales:**
- Prevención de solapes temporales con EXCLUDE constraints de PostgreSQL
- Sugerencia de slots rankeados por ML (probabilidad de asistencia)
- Control automático de periodicidad de prestaciones con alertas
- RBAC con 3 roles: admin, profesional, recepción
- Auditoría completa de acciones críticas
- Observabilidad con logging JSON estructurado

---

## Instalación Rápida

```bash
git clone https://github.com/clinica/agenda-clinica.git
cd agenda-clinica

poetry install

cp .env.example .env

alembic upgrade head

python -m app.scripts.seed_data

uvicorn app.presentacion.api_rest.main:app --reload
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

---

## Estructura del Proyecto

```
agenda-clinica/
├── app/
│   ├── presentacion/          # UI PyQt6 y API REST FastAPI
│   │   ├── ui_escritorio/     # Aplicación desktop
│   │   └── api_rest/          # Endpoints JSON
│   ├── aplicacion/            # Casos de uso y servicios
│   │   ├── servicios/         # AgendaService, AuthService, etc.
│   │   └── dtos/              # Request/Response DTOs
│   ├── dominio/               # Modelos ricos + invariantes
│   │   ├── entidades.py       # Usuario, Cita, Profesional, etc.
│   │   ├── valores.py         # Value objects inmutables
│   │   ├── reglas.py          # Validadores de negocio
│   │   └── repositorios.py    # Interfaces (Protocols)
│   ├── infraestructura/       # Implementaciones concretas
│   │   ├── db/                # SQLAlchemy models
│   │   ├── repos/             # Repositorios SQL
│   │   ├── seguridad/         # JWT, RBAC, hashing
│   │   └── logging/           # Logs estructurados
│   ├── analitica_ml/          # Pipeline ML
│   │   ├── features.py        # Feature engineering
│   │   ├── entrenamiento.py   # Training pipelines
│   │   ├── prediccion.py      # Scoring functions
│   │   └── almacenamiento_modelos.py
│   ├── config/                # Settings Pydantic
│   └── tests/                 # Tests unitarios e integración
├── alembic/                   # Migraciones de BD
├── docs/                      # Documentación adicional
├── pyproject.toml             # Poetry dependencies
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

---

## Comandos Make

```bash
make install    # Instalar dependencias
make test       # Ejecutar tests con cobertura
make lint       # Linter (ruff + mypy)
make format     # Formatear código (black + ruff)
make run        # Ejecutar API en modo desarrollo
make migrate    # Aplicar migraciones
make seed       # Poblar datos iniciales
make docker-up  # Levantar con Docker Compose
```

---

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────┐
│  PRESENTACIÓN                            │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  UI PyQt6    │  │  API FastAPI     │ │
│  └──────────────┘  └──────────────────┘ │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  APLICACIÓN (Servicios)                  │
│  - AgendaService                         │
│  - SesionesService                       │
│  - AlertasService                        │
│  - AuthService                           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  DOMINIO (Modelos + Reglas)             │
│  - Entidades con invariantes             │
│  - Value Objects inmutables              │
│  - Validadores de negocio                │
│  - Interfaces de repositorios            │
└─────────────────────────────────────────┘
        ▲               ▲
        │               │
┌───────┴──────┐  ┌────┴──────────────┐
│ INFRAESTRUC. │  │  ANALÍTICA ML     │
│ - DB/Repos   │  │  - Features       │
│ - Seguridad  │  │  - Entrenamiento  │
│ - Logging    │  │  - Predicción     │
└──────────────┘  └───────────────────┘
```

**Principios aplicados:**
- Inversión de dependencias: dominio no conoce infraestructura
- Separación de concerns: cada capa con responsabilidad única
- DDD: entidades ricas, value objects, agregados
- SOLID, KISS, DRY

---

## Entidades del Dominio

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Usuario** | Paciente/beneficiario | rut, nombre, fecha_nacimiento, nivel_apoyo[1\|2\|3] |
| **Profesional** | Terapeuta/médico | nombre, profesion, activo |
| **Box** | Sala/consultorio | nombre, ubicacion, activo |
| **Prestacion** | Tipo de servicio | nombre, duracion_minutos, periodicidad_dias, tolerancia_dias |
| **Cita** | Agendamiento | usuario, profesional, prestacion, box, inicio, fin, estado |
| **Bloqueo** | Restricción temporal | scope[box\|profesional], inicio, fin, motivo |
| **SesionRegistro** | Resultado de cita | cita_id, cumplida, valoracion, notas |
| **UsuarioSistema** | Usuario autenticado | email, password_hash, rol[admin\|profesional\|recepcion] |
| **Alerta** | Notificación control | usuario, prestacion, nivel[info\|warn\|crit], fecha_objetivo |
| **HorarioProfesional** | Disponibilidad | profesional, dia_semana, hora_inicio, hora_fin, box_preferido |

---

## API Endpoints Principales

### Autenticación
- `POST /auth/login` - Autenticar y obtener JWT
- `GET /auth/me` - Información del usuario actual

### Agenda
- `GET /agenda/sugerir-slots` - Obtener slots rankeados por ML
- `POST /agenda/asignar` - Asignar cita con validaciones
- `GET /agenda/citas` - Listar citas con filtros
- `PATCH /agenda/citas/{id}/estado` - Actualizar estado de cita

### Sesiones
- `POST /sesiones` - Registrar resultado de sesión
- `GET /sesiones/{cita_id}` - Obtener registro de sesión

### Analítica
- `GET /analitica/kpis` - Métricas: ocupación, no-show, throughput

### Alertas
- `GET /alertas` - Listar alertas pendientes
- `PATCH /alertas/{id}/resolver` - Marcar alerta como resuelta

### CRUD Básico
- `/usuarios`, `/profesionales`, `/boxes`, `/prestaciones`, `/bloqueos`

**Documentación completa:** Ver [API_ENDPOINTS.md](docs/API_ENDPOINTS.md)

---

## Validaciones de Negocio

### Validación de RUT Chileno
```python
def validar_rut(rut: str) -> bool:
    """Valida RUT con módulo 11"""
    # Formato: 12345678-5 o 7654321-K
    # Implementa algoritmo módulo 11
```

### Prevención de Solapes
```sql
-- PostgreSQL con EXCLUDE constraint
ALTER TABLE citas ADD CONSTRAINT no_solape_profesional 
  EXCLUDE USING gist (profesional_id WITH =, rango WITH &&)
  WHERE (estado IN ('programada', 'confirmada'));
```

### Control de Periodicidad
```python
def evaluar_control(usuario_id, prestacion_id):
    """
    Verifica si usuario tiene próxima cita dentro de ventana:
    [fecha_objetivo - tolerancia, fecha_objetivo + tolerancia]
    
    Si no existe, crea alerta según distancia:
    - crit: fuera de ventana
    - warn: dentro de ventana sin cita
    - info: próxima a ventana (7 días)
    """
```

---

## Machine Learning

### Modelo de Clasificación (Asistencia)
- **Objetivo:** Predecir probabilidad de asistencia a cita
- **Algoritmo:** GradientBoostingClassifier
- **Features:** dia_semana, hora, mes, edad, nivel_apoyo, duracion_minutos, periodicidad_dias
- **Métricas:** AUC-ROC >= 0.75, AUC-PR >= 0.70
- **Validación:** TimeSeriesSplit (3 folds)

### Modelo de Regresión (Demanda)
- **Objetivo:** Predecir ocupación por slot horario
- **Algoritmo:** RandomForestRegressor
- **Features:** dia_semana, hora, profesional_id
- **Métricas:** MAE < 2 citas, MAPE < 20%

### Scoring de Slots
Score combinado = 0.5 × p_asistencia + 0.3 × urgencia + 0.2 × ocupacion

Slots se ordenan descendentemente por score para sugerir mejores opciones.

---

## Seguridad

### RBAC (Control de Acceso Basado en Roles)
| Rol | Permisos |
|-----|----------|
| **admin** | Acceso completo, gestión de usuarios del sistema |
| **profesional** | Ver agenda propia, registrar sesiones, ver alertas |
| **recepcion** | Agendar citas, gestionar usuarios, ver agenda general |

### JWT (JSON Web Tokens)
- Expiración: 8 horas
- Claims: user_id, email, rol
- Algoritmo: HS256
- Secret rotable vía variable de entorno

### Hashing de Contraseñas
- bcrypt con factor de trabajo 12
- Salt único por contraseña

### Auditoría
Registro de eventos críticos:
- login, logout
- crear_cita, cancelar_cita
- registrar_sesion
- cambios de roles

---

## Observabilidad

### Logging Estructurado (JSON)
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "logger": "app.aplicacion.servicios.agenda_service",
  "request_id": "uuid",
  "user_id": "uuid",
  "rol": "recepcion",
  "event": "cita_asignada",
  "cita_id": "uuid",
  "usuario_id": "uuid",
  "profesional_id": "uuid"
}
```

### Métricas (Prometheus)
- requests_total (labels: método, endpoint, status)
- request_duration_seconds (histograma)
- citas_creadas_total (contador)
- usuarios_activos (gauge)
- alertas_pendientes (gauge)

### Healthchecks
- `GET /health` - Status general
- `GET /health/db` - Conectividad BD

---

## Despliegue

### Docker Compose (Desarrollo)
```bash
docker-compose up -d
```

Servicios:
- **db**: PostgreSQL 15
- **api**: FastAPI con hot-reload
- **redis** (opcional): Caché

### Producción
1. Build imagen Docker
2. Aplicar migraciones: `alembic upgrade head`
3. Ejecutar API: `uvicorn app.presentacion.api_rest.main:app --host 0.0.0.0 --port 8000`
4. Configurar reverse proxy (nginx/traefik)
5. Configurar backups automáticos
6. Monitoreo con Prometheus + Grafana

### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=secreto-seguro-cambiar
CORS_ORIGINS=["https://app.clinica.cl"]
ENABLE_ML_SCORING=true
```

---

## Testing

### Cobertura Objetivo: >80%

```bash
poetry run pytest tests/ -v --cov=app --cov-report=html
```

### Tests Unitarios
- Validadores (RUT, periodicidad, solapes)
- Entidades con invariantes
- Reglas de negocio

### Tests de Integración
- Repositorios con BD de prueba
- Endpoints API completos
- Flujos end-to-end

---

## Roadmap

### Fase 1: MVP (4-6 semanas)
- [x] Arquitectura base y modelos
- [x] CRUD usuarios, profesionales, boxes, prestaciones
- [x] Agenda básica con validación de solapes
- [x] Autenticación JWT + RBAC
- [ ] UI PyQt6 básica

### Fase 2: Features Core (6-8 semanas)
- [ ] Sugerencia de slots con filtros
- [ ] Control de periodicidad y alertas
- [ ] Registro de sesiones
- [ ] Dashboard analítico básico

### Fase 3: ML e Inteligencia (4-6 semanas)
- [ ] Pipeline de features
- [ ] Entrenamiento de modelos
- [ ] Scoring ML de slots
- [ ] Reentrenamiento automático

### Fase 4: Optimización (continuo)
- [ ] Caché Redis
- [ ] Optimización de queries
- [ ] Monitoreo avanzado
- [ ] Escalamiento horizontal

---

## Contribución

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

**Estándares de código:**
- PEP 8
- Type hints obligatorios
- Tests para nueva funcionalidad
- Coverage >80%
- Linting sin errores (`make lint`)

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Soporte

- Documentación técnica: [docs/](docs/)
- Issues: https://github.com/clinica/agenda-clinica/issues
- Email: dev@clinica.cl

---

## Autores

Equipo de Desarrollo - Clínica XYZ

**Versión:** 1.0.0  
**Última actualización:** Enero 2025
