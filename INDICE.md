# Índice de Documentación - Sistema de Agenda Clínica

Esta documentación contiene toda la especificación técnica, código base y guías de implementación para el Sistema de Agenda Clínica con asignación dinámica y analítica ML.

---

## Documentos Disponibles

### 1. [README.md](computer:///mnt/user-data/outputs/README.md)
**Para:** Desarrolladores y usuarios técnicos  
**Contenido:**
- Instalación rápida y setup
- Arquitectura de alto nivel
- Estructura del proyecto
- Comandos principales (Make)
- Entidades del dominio
- Endpoints de API
- Guía de contribución

**Recomendado como:** Punto de partida para el equipo de desarrollo

---

### 2. [RESUMEN_EJECUTIVO.md](computer:///mnt/user-data/outputs/RESUMEN_EJECUTIVO.md)
**Para:** Stakeholders, gerencia, product owners  
**Contenido:**
- Visión general del sistema
- Problemas que resuelve
- Valor de negocio y ROI
- Funcionalidades clave por rol
- Indicadores de éxito
- Costos estimados (desarrollo y operación)
- Plan de implementación por fases
- Riesgos y mitigaciones

**Recomendado como:** Presentación para aprobación de proyecto

---

### 3. [CODIGO_BASE.md](computer:///mnt/user-data/outputs/CODIGO_BASE.md)
**Para:** Desarrolladores Python  
**Contenido:**
- Código completo del dominio (entidades, value objects, reglas)
- Interfaces de repositorios (Protocols)
- Validadores implementados (RUT, solapes, periodicidad)
- Tests unitarios completos con ejemplos
- Ejemplos de uso del código

**Recomendado como:** Referencia de implementación y base de código

---

### 4. [CONFIGURACION_DESPLIEGUE.md](computer:///mnt/user-data/outputs/CONFIGURACION_DESPLIEGUE.md)
**Para:** DevOps, SRE, desarrolladores  
**Contenido:**
- Settings con Pydantic
- Variables de entorno (.env.example)
- Dockerfile optimizado
- docker-compose (desarrollo y producción)
- Makefile con comandos útiles
- pyproject.toml completo
- nginx.conf para producción
- Scripts de deployment y backup
- Script de seed data

**Recomendado como:** Guía de despliegue y configuración

---

## Mapa de Navegación por Rol

### Si eres Product Owner / Manager
1. Lee primero: [RESUMEN_EJECUTIVO.md](computer:///mnt/user-data/outputs/RESUMEN_EJECUTIVO.md)
2. Revisa arquitectura en: [README.md](computer:///mnt/user-data/outputs/README.md) (sección Arquitectura)
3. Valida funcionalidades vs requisitos

### Si eres Desarrollador Backend
1. Lee primero: [README.md](computer:///mnt/user-data/outputs/README.md)
2. Revisa código base: [CODIGO_BASE.md](computer:///mnt/user-data/outputs/CODIGO_BASE.md)
3. Setup local: [CONFIGURACION_DESPLIEGUE.md](computer:///mnt/user-data/outputs/CONFIGURACION_DESPLIEGUE.md)
4. Implementa siguiendo patrones del código base

### Si eres DevOps / SRE
1. Lee despliegue: [CONFIGURACION_DESPLIEGUE.md](computer:///mnt/user-data/outputs/CONFIGURACION_DESPLIEGUE.md)
2. Revisa arquitectura: [README.md](computer:///mnt/user-data/outputs/README.md) (sección Despliegue)
3. Configura CI/CD según Makefile
4. Implementa monitoreo y backups

### Si eres QA / Tester
1. Lee funcionalidades: [README.md](computer:///mnt/user-data/outputs/README.md) (sección Entidades y Endpoints)
2. Revisa casos de prueba: [CODIGO_BASE.md](computer:///mnt/user-data/outputs/CODIGO_BASE.md) (sección Tests)
3. Valida reglas de negocio en código base
4. Define casos de prueba adicionales

---

## Arquitectura en Resumen

```
┌─────────────────────────────────────────┐
│  PRESENTACIÓN                            │
│  - UI PyQt6 (desktop)                   │
│  - API REST FastAPI                     │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  APLICACIÓN                              │
│  - AgendaService                         │
│  - SesionesService                       │
│  - AlertasService                        │
│  - AuthService                           │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  DOMINIO                                 │
│  - Entidades (Usuario, Cita, etc.)      │
│  - Value Objects (RUT, Periodicidad)    │
│  - Reglas de negocio                    │
│  - Interfaces de repositorios           │
└─────────────────────────────────────────┘
        ▲               ▲
        │               │
┌───────┴──────┐  ┌────┴──────────────┐
│ INFRAESTRUC. │  │  ANALÍTICA ML     │
│ - PostgreSQL │  │  - Features       │
│ - Repos SQL  │  │  - Entrenamiento  │
│ - JWT/RBAC   │  │  - Predicción     │
│ - Logging    │  │                   │
└──────────────┘  └───────────────────┘
```

---

## Stack Tecnológico

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- SQLAlchemy 2.0 (ORM)
- Alembic (migraciones)
- Pydantic V2 (validación)

**Base de datos:**
- PostgreSQL 15 (producción)
- SQLite (desarrollo)
- Redis (caché opcional)

**Frontend:**
- PyQt6 (UI desktop)

**Machine Learning:**
- scikit-learn
- pandas
- joblib

**Infraestructura:**
- Docker / Docker Compose
- nginx (reverse proxy)
- Poetry (gestión dependencias)

**Calidad:**
- pytest (testing)
- black (formatter)
- ruff (linter)
- mypy (type checker)

---

## Quick Start (5 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/clinica/agenda-clinica.git
cd agenda-clinica

# 2. Instalar dependencias
make install

# 3. Configurar .env
cp .env.example .env

# 4. Levantar con Docker
make docker-up

# 5. Acceder
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## Componentes Principales

### Entidades del Dominio
- **Usuario**: Paciente/beneficiario con RUT chileno
- **Profesional**: Terapeuta o médico
- **Box**: Sala o consultorio
- **Prestacion**: Tipo de servicio (kinesiología, fonoaudiología, etc.)
- **Cita**: Agendamiento con validación de solapes
- **SesionRegistro**: Resultado de cita (asistencia, valoración)
- **Alerta**: Notificación de usuario fuera de control
- **HorarioProfesional**: Disponibilidad por día de semana

### Validaciones Críticas
- RUT chileno (módulo 11)
- Prevención de solapes (PostgreSQL EXCLUDE constraint)
- Control de periodicidad (ventana de tolerancia)
- RBAC (admin, profesional, recepción)

### Machine Learning
- **Clasificador de asistencia**: Predice probabilidad de no-show
- **Regresor de demanda**: Anticipa ocupación por horario
- **Scoring combinado**: 0.5×asistencia + 0.3×urgencia + 0.2×ocupación

---

## Checklist de Implementación

### Fase 1: MVP (6-8 semanas)
- [ ] Setup de proyecto y dependencias
- [ ] Modelos del dominio con invariantes
- [ ] Repositorios e infraestructura BD
- [ ] CRUD básico de entidades
- [ ] API REST con autenticación JWT
- [ ] Validación de solapes
- [ ] Tests unitarios >80% cobertura

### Fase 2: Features Core (8-10 semanas)
- [ ] Sugerencia de slots
- [ ] Sistema de alertas automáticas
- [ ] Registro de sesiones
- [ ] Dashboard analítico con KPIs
- [ ] UI PyQt6 completa
- [ ] Tests de integración

### Fase 3: ML (6-8 semanas)
- [ ] Pipeline de features
- [ ] Entrenamiento de modelos
- [ ] Scoring automático de slots
- [ ] Reentrenamiento programado
- [ ] Monitoreo de predicciones

### Fase 4: Optimización
- [ ] Caché con Redis
- [ ] Optimización de queries
- [ ] Monitoreo con Prometheus/Grafana
- [ ] Escalamiento horizontal
- [ ] Documentación completa

---

## Métricas de Éxito

### Técnicas
- Cobertura de tests: >80%
- Disponibilidad: >99.5%
- Tiempo de respuesta p95: <200ms
- Despliegue: <5 minutos
- Cero pérdida de datos

### Negocio
- Reducción de no-shows: 20-30%
- Aumento de ocupación: 15-25%
- Usuarios bajo control: >90%
- Tiempo de agendamiento: <2 minutos
- ROI: 4-6 meses

---

## Soporte y Contacto

**Documentación adicional:**
- Swagger/OpenAPI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

**Repositorio:**
- GitHub: https://github.com/clinica/agenda-clinica
- Issues: https://github.com/clinica/agenda-clinica/issues

**Equipo:**
- Email: dev@clinica.cl
- Slack: #agenda-clinica

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Próximos Pasos Recomendados

1. **Revisar documentación completa** en el orden sugerido según tu rol
2. **Setup de ambiente local** siguiendo README.md
3. **Implementar MVP** comenzando por el dominio (CODIGO_BASE.md)
4. **Configurar CI/CD** siguiendo CONFIGURACION_DESPLIEGUE.md
5. **Validar con usuarios** piloto antes de go-live
6. **Iterar** basándose en feedback real

---

**Versión de documentación:** 1.0  
**Fecha de generación:** Noviembre 2025  
**Autor:** Equipo de Arquitectura de Software
