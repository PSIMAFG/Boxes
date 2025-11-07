# 📁 ESTRUCTURA DE CARPETAS DEL PROYECTO

**Proyecto:** Sistema de Agenda Clínica
**Versión:** 1.0

---

## Estructura Completa

```
Boxes/
│
├── 📁 frontend/                          # Frontend React SPA
│   ├── 📁 public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── 📁 src/
│   │   ├── 📁 assets/                    # Imágenes, fuentes, estilos globales
│   │   │   ├── logo.svg
│   │   │   └── styles/
│   │   │       └── global.css
│   │   │
│   │   ├── 📁 components/                # Componentes reutilizables
│   │   │   ├── 📁 common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── Alert.tsx
│   │   │   │
│   │   │   ├── 📁 layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Layout.tsx
│   │   │   │
│   │   │   └── 📁 forms/
│   │   │       ├── LoginForm.tsx
│   │   │       ├── RegistroForm.tsx
│   │   │       └── FormField.tsx
│   │   │
│   │   ├── 📁 pages/                     # Páginas principales
│   │   │   ├── 📁 auth/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── RegistroPage.tsx
│   │   │   │   ├── RegistroExitosoPage.tsx
│   │   │   │   └── RecuperarPasswordPage.tsx
│   │   │   │
│   │   │   ├── 📁 dashboard/
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── AdminDashboard.tsx
│   │   │   │   ├── ProfesionalDashboard.tsx
│   │   │   │   └── AdministrativoDashboard.tsx
│   │   │   │
│   │   │   ├── 📁 usuarios-sistema/
│   │   │   │   ├── UsuariosPendientesPage.tsx
│   │   │   │   ├── UsuariosListaPage.tsx
│   │   │   │   ├── AprobarUsuarioModal.tsx
│   │   │   │   └── CrearUsuarioPage.tsx
│   │   │   │
│   │   │   ├── 📁 pacientes/
│   │   │   │   ├── PacientesListaPage.tsx
│   │   │   │   ├── PacienteDetallePage.tsx
│   │   │   │   ├── PacienteCrearPage.tsx
│   │   │   │   └── PacienteHistorialPage.tsx
│   │   │   │
│   │   │   ├── 📁 boxes/
│   │   │   │   ├── BoxesListaPage.tsx
│   │   │   │   ├── BoxCrearPage.tsx
│   │   │   │   └── BoxDisponibilidadPage.tsx
│   │   │   │
│   │   │   ├── 📁 agenda/
│   │   │   │   ├── AgendaCalendarioPage.tsx
│   │   │   │   ├── CitaCrearPage.tsx
│   │   │   │   ├── CitaDetallePage.tsx
│   │   │   │   └── MisCitasPage.tsx
│   │   │   │
│   │   │   ├── 📁 atenciones/
│   │   │   │   ├── AtencionesListaPage.tsx
│   │   │   │   ├── RegistrarAtencionPage.tsx
│   │   │   │   └── AtencionDetallePage.tsx
│   │   │   │
│   │   │   ├── 📁 reportes/
│   │   │   │   ├── ReportesPage.tsx
│   │   │   │   ├── ReporteAtencionesProfesional.tsx
│   │   │   │   ├── ReporteOcupacionBoxes.tsx
│   │   │   │   └── ReporteValoraciones.tsx
│   │   │   │
│   │   │   └── 📁 perfil/
│   │   │       ├── PerfilPage.tsx
│   │   │       ├── CambiarPasswordPage.tsx
│   │   │       └── ActividadPage.tsx
│   │   │
│   │   ├── 📁 hooks/                     # Custom React Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useFetch.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   └── useDebounce.ts
│   │   │
│   │   ├── 📁 context/                   # React Context (State Management)
│   │   │   ├── AuthContext.tsx
│   │   │   ├── ThemeContext.tsx
│   │   │   └── NotificationContext.tsx
│   │   │
│   │   ├── 📁 guards/                    # Route Guards
│   │   │   ├── PrivateRoute.tsx
│   │   │   ├── RoleGuard.tsx
│   │   │   └── PublicRoute.tsx
│   │   │
│   │   ├── 📁 services/                  # API Services
│   │   │   ├── api.ts                    # Axios instance con interceptores
│   │   │   ├── authService.ts
│   │   │   ├── pacientesService.ts
│   │   │   ├── boxesService.ts
│   │   │   ├── citasService.ts
│   │   │   └── atencionesService.ts
│   │   │
│   │   ├── 📁 types/                     # TypeScript Types/Interfaces
│   │   │   ├── auth.types.ts
│   │   │   ├── paciente.types.ts
│   │   │   ├── box.types.ts
│   │   │   ├── cita.types.ts
│   │   │   └── common.types.ts
│   │   │
│   │   ├── 📁 utils/                     # Utilidades
│   │   │   ├── validators.ts
│   │   │   ├── formatters.ts
│   │   │   ├── constants.ts
│   │   │   └── permissions.ts
│   │   │
│   │   ├── 📁 routes/                    # Configuración de rutas
│   │   │   └── AppRoutes.tsx
│   │   │
│   │   ├── App.tsx                       # Componente raíz
│   │   ├── index.tsx                     # Entry point
│   │   └── vite-env.d.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
│
├── 📁 app/                               # Backend FastAPI
│   │
│   ├── 📁 dominio/                       # Capa de dominio (DDD)
│   │   ├── __init__.py
│   │   ├── entidades.py                  # Entidades de negocio
│   │   ├── valores.py                    # Value Objects
│   │   ├── repositorios.py               # Interfaces abstractas de repos
│   │   └── reglas.py                     # Reglas de negocio
│   │
│   ├── 📁 aplicacion/                    # Capa de aplicación
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 dtos/                      # Data Transfer Objects
│   │   │   ├── __init__.py
│   │   │   ├── auth_dto.py
│   │   │   ├── usuario_dto.py
│   │   │   ├── paciente_dto.py
│   │   │   ├── box_dto.py
│   │   │   ├── cita_dto.py
│   │   │   ├── atencion_dto.py
│   │   │   └── comunes_dto.py
│   │   │
│   │   └── 📁 servicios/                 # Servicios de aplicación
│   │       ├── __init__.py
│   │       ├── auth_service.py           # Login, registro, aprobación, JWT
│   │       ├── usuario_service.py
│   │       ├── paciente_service.py
│   │       ├── box_service.py
│   │       ├── agenda_service.py
│   │       ├── atencion_service.py
│   │       ├── reporte_service.py
│   │       └── alertas_service.py
│   │
│   ├── 📁 infraestructura/               # Capa de infraestructura
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 db/                        # Base de datos
│   │   │   ├── __init__.py
│   │   │   ├── database.py               # Configuración SQLAlchemy + get_db
│   │   │   └── models.py                 # Modelos SQLAlchemy
│   │   │
│   │   ├── 📁 repos/                     # Implementación de repositorios
│   │   │   ├── __init__.py
│   │   │   ├── usuario_sistema_repo.py
│   │   │   ├── paciente_repo.py
│   │   │   ├── profesional_repo.py
│   │   │   ├── box_repo.py
│   │   │   ├── prestacion_repo.py
│   │   │   ├── agenda_repo.py
│   │   │   ├── sesiones_repo.py
│   │   │   ├── alertas_repo.py
│   │   │   ├── auditoria_repo.py
│   │   │   └── refresh_token_repo.py     # Nuevo: para refresh tokens
│   │   │
│   │   ├── 📁 seguridad/                 # Seguridad
│   │   │   ├── __init__.py
│   │   │   ├── hashing.py                # bcrypt para passwords
│   │   │   ├── jwt.py                    # Generar y verificar JWT
│   │   │   ├── rbac.py                   # Control de acceso basado en roles
│   │   │   └── permissions.py            # Matriz de permisos detallada
│   │   │
│   │   └── 📁 logging/                   # Logging y auditoría
│   │       ├── __init__.py
│   │       └── logger.py
│   │
│   ├── 📁 presentacion/                  # Capa de presentación
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 api_rest/                  # API REST
│   │   │   ├── __init__.py
│   │   │   ├── main.py                   # Aplicación FastAPI principal
│   │   │   ├── dependencias.py           # Dependencias compartidas
│   │   │   │
│   │   │   └── 📁 routers/               # Routers por módulo
│   │   │       ├── __init__.py
│   │   │       ├── auth_router.py        # /auth/*
│   │   │       ├── usuarios_router.py    # /usuarios-sistema/*
│   │   │       ├── pacientes_router.py   # /pacientes/*
│   │   │       ├── boxes_router.py       # /boxes/*
│   │   │       ├── citas_router.py       # /citas/*
│   │   │       ├── atenciones_router.py  # /atenciones/*
│   │   │       ├── reportes_router.py    # /reportes/*
│   │   │       └── perfil_router.py      # /perfil/*
│   │   │
│   │   └── 📁 ui_escritorio/             # Interfaz PyQt6 (opcional)
│   │       ├── __init__.py
│   │       ├── main_window.py
│   │       └── 📁 ventanas/
│   │           ├── login_window.py
│   │           ├── dashboard_window.py
│   │           └── pacientes_window.py
│   │
│   ├── 📁 config/                        # Configuración
│   │   ├── __init__.py
│   │   └── settings.py                   # Variables de entorno, secrets
│   │
│   ├── 📁 tests/                         # Tests
│   │   ├── __init__.py
│   │   ├── 📁 unit/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_paciente_service.py
│   │   │   └── test_reglas.py
│   │   │
│   │   └── 📁 integration/
│   │       ├── test_auth_router.py
│   │       └── test_pacientes_router.py
│   │
│   ├── 📁 scripts/                       # Scripts de utilidad
│   │   ├── __init__.py
│   │   ├── seed_data.py                  # Poblar datos de prueba
│   │   └── crear_admin.py                # Crear usuario admin inicial
│   │
│   └── main.py                           # Entry point del backend
│
├── 📁 alembic/                           # Migraciones de BD
│   ├── versions/
│   │   ├── 20250106_initial_schema.py
│   │   ├── 20250107_box_enhancements.py
│   │   └── 20250108_add_refresh_tokens.py  # Nueva migración
│   ├── env.py
│   └── script.py.mako
│
├── 📁 docs/                              # Documentación
│   ├── ARQUITECTURA_AGENDA_CLINICA.md
│   ├── ESTRUCTURA_CARPETAS.md
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
│
├── 📄 .env.example                       # Variables de entorno ejemplo
├── 📄 .gitignore
├── 📄 alembic.ini
├── 📄 pyproject.toml                     # Dependencias Python
├── 📄 README.md
├── 📄 Dockerfile
├── 📄 docker-compose.yml
└── 📄 Makefile
```

---

## Decisiones de Estructura

### Frontend (React)
- **Vite** como bundler (más rápido que CRA)
- **TypeScript** para type safety
- **React Router v6** para routing
- **Context API** para state (o Redux si crece)
- **Axios** para peticiones HTTP con interceptores
- **TailwindCSS** o **MUI** para estilos
- Separación clara: pages, components, services, guards

### Backend (FastAPI)
- **Clean Architecture** estricta
- **Dominio** independiente de frameworks
- **Aplicación** orquesta casos de uso
- **Infraestructura** implementa detalles técnicos
- **Presentación** múltiple: REST + PyQt6 (opcional)

### Base de Datos
- **PostgreSQL** como principal
- **SQLAlchemy** ORM
- **Alembic** para migraciones versionadas
- Modelos separados de entidades de dominio

---

✅ **Estructura completa definida**
