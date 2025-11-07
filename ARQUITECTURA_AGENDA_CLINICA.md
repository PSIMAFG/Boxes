# 🏥 ARQUITECTURA DEL SISTEMA DE AGENDA CLÍNICA

**Versión:** 1.0
**Fecha:** 2025-11-07
**Estado:** Diseño Completo y Robusto

---

## [1] PLAN RESUMIDO Y ARQUITECTURA

### 1.1 Visión General del Sistema

Sistema de gestión de agenda clínica con **autenticación JWT**, **registro con aprobación**, **RBAC** (Control de Acceso Basado en Roles) y módulos especializados para la gestión de pacientes, boxes, atenciones y reportes.

**Principios Arquitectónicos:**
- **Clean Architecture**: Separación de dominio, aplicación, infraestructura y presentación
- **DDD (Domain-Driven Design)**: Entidades, agregados y reglas de negocio en el dominio
- **SOLID**: Inyección de dependencias, responsabilidad única
- **Security by Design**: Validación en capas, auditoría completa
- **API-First**: Backend REST con FastAPI, frontend desacoplado

---

### 1.2 Arquitectura de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTACIÓN                            │
│  ┌────────────────────┐        ┌──────────────────────┐    │
│  │   Frontend React   │   OR   │   PyQt6 Desktop UI   │    │
│  │  - Guards/Routing  │        │  - Role-based Views  │    │
│  │  - State Mgmt      │        │  - Qt Signals/Slots  │    │
│  └────────────────────┘        └──────────────────────┘    │
│              │                            │                  │
│              └────────────────────────────┘                  │
│                           ↓                                  │
│              ┌─────────────────────────┐                    │
│              │   FastAPI REST API      │                    │
│              │   (routers/*.py)        │                    │
│              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      APLICACIÓN                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Servicios de Aplicación (DTOs + Lógica de Casos)   │  │
│  │  - AuthService    - UsuarioService                   │  │
│  │  - AgendaService  - AtencionService                  │  │
│  │  - BoxService     - ReporteService                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                        DOMINIO                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Entidades + Reglas de Negocio + Repositorios (ABC) │  │
│  │  - Usuario, Paciente, Box, Cita, Sesion             │  │
│  │  - Validaciones de negocio                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    INFRAESTRUCTURA                           │
│  ┌──────────────────┬────────────────┬──────────────────┐  │
│  │  Persistencia    │   Seguridad    │    Logging       │  │
│  │  - SQLAlchemy    │   - JWT        │    - Auditoria   │  │
│  │  - Alembic       │   - bcrypt     │    - Logger      │  │
│  │  - Repos         │   - RBAC       │                  │  │
│  └──────────────────┴────────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 1.3 Flujo de Autenticación y Registro

```
┌──────────────────────────────────────────────────────────────────┐
│                   FLUJO DE REGISTRO Y APROBACIÓN                  │
└──────────────────────────────────────────────────────────────────┘

1. REGISTRO PÚBLICO
   Usuario → POST /auth/registro
           → email, password, nombre
           → Estado: "pendiente"
           → Email de confirmación (opcional)

2. APROBACIÓN POR ADMIN
   Admin → GET /auth/usuarios-pendientes
         → Lista de usuarios en espera
   Admin → POST /auth/aprobar/{user_id}
         → Asigna rol: admin | profesional | administrativo
         → Estado: "activo"
         → Notificación al usuario

3. LOGIN
   Usuario → POST /auth/login
           → email, password
           → Verifica estado = "activo"
           → Genera: access_token (15 min) + refresh_token (7 días)
           → Retorna: LoginResponseDTO

4. REFRESH TOKEN
   Usuario → POST /auth/refresh
           → refresh_token
           → Genera nuevo access_token
           → Opcional: Rota refresh_token

5. ACCESO PROTEGIDO
   Usuario → GET /api/pacientes
           → Header: Authorization Bearer {access_token}
           → RBAC: Verifica rol permitido
           → Ejecuta operación
```

---

### 1.4 Modelo de Roles y Permisos (RBAC)

```python
# Matriz de Permisos

PERMISOS = {
    "admin": {
        "usuarios_sistema": ["crear", "listar", "aprobar", "editar", "desactivar"],
        "pacientes": ["crear", "listar", "editar", "eliminar"],
        "boxes": ["crear", "listar", "editar", "eliminar"],
        "prestaciones": ["crear", "listar", "editar", "eliminar"],
        "profesionales": ["crear", "listar", "editar", "eliminar"],
        "citas": ["crear", "listar", "editar", "eliminar"],
        "atenciones": ["registrar", "listar", "editar"],
        "reportes": ["ver_todos", "exportar"]
    },
    "profesional": {
        "pacientes": ["crear_demografico", "listar", "ver_detalle"],
        "boxes": ["listar", "ver_disponibilidad"],
        "citas": ["listar_propias", "ver_detalle"],
        "atenciones": ["registrar_propias", "listar_propias"],
        "reportes": ["ver_propios"]
    },
    "administrativo": {
        "pacientes": ["listar", "ver_detalle"],
        "boxes": ["listar"],
        "prestaciones": ["listar"],
        "profesionales": ["listar"],
        "citas": ["listar", "ver_detalle"],
        "atenciones": ["listar"],
        "reportes": ["ver_generales"]
    }
}
```

**Reglas Especiales:**
- **Profesional** solo puede registrar atenciones para sus propias citas
- **Profesional** solo puede crear pacientes con datos demográficos básicos (sin historial clínico completo)
- **Administrativo** es solo lectura, sin modificaciones
- **Admin** tiene acceso total, incluye aprobación de usuarios

---

### 1.5 Seguridad JWT

```yaml
Access Token:
  - Duración: 15 minutos
  - Algoritmo: HS256 (JWT estándar)
  - Claims: user_id, email, rol, exp, iat
  - Almacenamiento: Memory (frontend) o HttpOnly Cookie

Refresh Token:
  - Duración: 7 días
  - Algoritmo: HS256
  - Claims: user_id, token_family, exp, iat
  - Almacenamiento: HttpOnly Cookie (más seguro)
  - Rotación: Opcional - genera nuevo refresh en cada uso
  - Revocación: Tabla refresh_tokens con campo revoked

Configuración:
  - SECRET_KEY: 32+ caracteres aleatorios
  - ALGORITHM: HS256
  - REFRESH_SECRET_KEY: Clave diferente para refresh tokens
```

---

### 1.6 Módulos Funcionales

#### **Módulo de Autenticación**
- Login, logout, registro, aprobación
- Refresh token, cambio de contraseña
- Recuperación de contraseña (email)

#### **Módulo de Pacientes**
- CRUD de pacientes (datos demográficos)
- Búsqueda por RUT, nombre
- Historial de atenciones
- Alertas de control

#### **Módulo de Boxes**
- CRUD de boxes/consultorios
- Disponibilidad en tiempo real
- Asignación de profesionales

#### **Módulo de Citas/Agenda**
- Programación de citas
- Visualización de agenda (día, semana, mes)
- Estados: programada, confirmada, cumplida, no_asistio, cancelada
- Conflictos de horarios

#### **Módulo de Atenciones**
- Registro de sesión realizada
- Valoración: positivo (+) / neutro (0) / negativo (–)
- Notas clínicas (solo profesional)

#### **Módulo de Reportes**
- Atenciones por profesional
- Ocupación de boxes
- Estadísticas de valoraciones
- Exportación: PDF, Excel, CSV

#### **Módulo de Perfil**
- Ver/editar datos personales
- Cambiar contraseña
- Historial de actividad (auditoría)

---

## [2] MAPA DEL SITIO Y RUTAS FRONTEND

### 2.1 Rutas Públicas

```
/                        → Landing page / Redirect to login
/login                   → Formulario de login
/registro                → Formulario de registro
/registro-exitoso        → Mensaje: "Espera aprobación del admin"
/recuperar-password      → Solicitar reset de contraseña
/reset-password/:token   → Formulario con token
```

---

### 2.2 Rutas Privadas (Protegidas)

#### **Dashboard Principal**
```
/dashboard               → Vista principal según rol
  - Admin: Métricas generales + acceso a todo
  - Profesional: Agenda del día + pacientes asignados
  - Administrativo: Vista de consulta general
```

#### **Módulo de Usuarios Sistema** (Solo Admin)
```
/usuarios-sistema
  /usuarios-sistema/pendientes      → Lista de usuarios por aprobar
  /usuarios-sistema/aprobar/:id     → Modal de aprobación + asignar rol
  /usuarios-sistema/lista           → Lista de usuarios activos
  /usuarios-sistema/crear           → Crear usuario directamente
  /usuarios-sistema/:id/editar      → Editar usuario
```

#### **Módulo de Pacientes**
```
/pacientes
  /pacientes/lista                  → Tabla con búsqueda
  /pacientes/crear                  → Formulario (profesional: solo demografía)
  /pacientes/:id                    → Detalle completo
  /pacientes/:id/editar             → Editar (según rol)
  /pacientes/:id/historial          → Historial de atenciones
```

#### **Módulo de Boxes** (Admin + Profesional lectura)
```
/boxes
  /boxes/lista                      → Tabla de boxes
  /boxes/crear                      → Formulario (solo admin)
  /boxes/:id/editar                 → Editar (solo admin)
  /boxes/disponibilidad             → Vista de ocupación
```

#### **Módulo de Agenda/Citas**
```
/agenda
  /agenda/calendario                → Vista calendario (día/semana/mes)
  /agenda/crear-cita                → Formulario de nueva cita
  /agenda/cita/:id                  → Detalle de cita
  /agenda/cita/:id/editar           → Editar cita
  /agenda/mis-citas                 → Citas del profesional logueado
```

#### **Módulo de Atenciones**
```
/atenciones
  /atenciones/lista                 → Tabla de sesiones registradas
  /atenciones/registrar/:cita_id    → Formulario: cumplida, valoración, notas
  /atenciones/:id                   → Ver detalle (solo profesional owner o admin)
```

#### **Módulo de Reportes**
```
/reportes
  /reportes/atenciones-profesional  → Reporte por profesional
  /reportes/ocupacion-boxes         → Reporte de boxes
  /reportes/valoraciones            → Estadísticas de valoraciones
  /reportes/alertas                 → Pacientes fuera de control
```

#### **Módulo de Perfil**
```
/perfil
  /perfil/info                      → Datos personales
  /perfil/cambiar-password          → Cambio de contraseña
  /perfil/actividad                 → Log de auditoría del usuario
```

---

### 2.3 Matriz de Rutas por Rol

| Ruta                          | Admin | Profesional | Administrativo |
|-------------------------------|-------|-------------|----------------|
| /dashboard                    | ✅    | ✅          | ✅             |
| /usuarios-sistema/*           | ✅    | ❌          | ❌             |
| /pacientes/crear              | ✅    | ✅*         | ❌             |
| /pacientes/lista              | ✅    | ✅          | ✅             |
| /pacientes/:id                | ✅    | ✅          | ✅             |
| /pacientes/:id/editar         | ✅    | ❌          | ❌             |
| /boxes/crear                  | ✅    | ❌          | ❌             |
| /boxes/lista                  | ✅    | ✅          | ✅             |
| /agenda/crear-cita            | ✅    | ❌          | ❌             |
| /agenda/calendario            | ✅    | ✅          | ✅             |
| /atenciones/registrar         | ✅    | ✅*         | ❌             |
| /atenciones/lista             | ✅    | ✅*         | ✅             |
| /reportes/*                   | ✅    | ✅*         | ✅*            |

**Notas:**
- ✅* = Acceso limitado (e.g., profesional ve solo sus atenciones)
- Profesional crea pacientes sin historial clínico completo
- Administrativo es 100% lectura

---

