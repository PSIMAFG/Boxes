# 📂 Estructura del Proyecto Frontend PyQt6

## 🗂️ Árbol de Directorios

```
frontend_pyqt/
│
├── 📄 main.py                      # Punto de entrada de la aplicación
├── 📄 requirements.txt             # Dependencias Python
├── 📄 .env                         # Configuración (no versionado)
├── 📄 .env.example                 # Ejemplo de configuración
├── 📄 .gitignore                   # Archivos ignorados por git
├── 📄 README.md                    # Documentación completa
├── 📄 QUICKSTART.md                # Guía de inicio rápido
├── 📄 ESTRUCTURA.md                # Este archivo
│
├── 📁 controllers/                 # Lógica de negocio y controladores
│   ├── __init__.py
│   ├── api_client.py              # Cliente HTTP con manejo JWT
│   ├── auth_controller.py         # Controlador de autenticación
│   ├── user_state.py              # Gestión de estado de sesión
│   ├── role_guard.py              # Control de acceso basado en roles
│   ├── navigation.py              # Sistema de navegación entre vistas
│   ├── validators.py              # Validadores de formularios
│   └── errors.py                  # Manejo centralizado de errores
│
├── 📁 ui/                          # Interfaces de usuario (ventanas)
│   ├── __init__.py
│   ├── login_window.py            # Ventana de login
│   ├── register_window.py         # Ventana de registro
│   ├── dashboard_window.py        # Dashboard principal con navegación
│   ├── inicio_view.py             # Vista de inicio/home
│   ├── perfil_window.py           # Ventana de perfil de usuario
│   ├── usuarios_window.py         # Gestión de usuarios (admin)
│   ├── pacientes_window.py        # Gestión de pacientes
│   ├── boxes_window.py            # Gestión de boxes
│   ├── atenciones_window.py       # Gestión de atenciones
│   └── reportes_window.py         # Vista de reportes
│
├── 📁 resources/                   # Recursos y constantes
│   ├── __init__.py
│   ├── constants.py               # Constantes globales
│   └── styles.qss                 # Estilos Qt (CSS-like)
│
└── 📁 scripts/                     # Scripts de utilidad
    ├── __init__.py
    ├── generate_key.py            # Generador de clave de cifrado
    └── check_setup.py             # Verificador de configuración
```

## 📋 Descripción de Archivos Principales

### 🎯 Punto de Entrada

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Aplicación principal. Configura event loop asyncio, carga estilos, maneja navegación entre login y dashboard |

### 🎮 Controladores

| Archivo | Responsabilidad | Dependencias |
|---------|-----------------|--------------|
| `api_client.py` | Cliente HTTP para backend. Maneja refresh automático de JWT | httpx, user_state |
| `auth_controller.py` | Login, registro, logout, refresh de sesión | api_client, user_state |
| `user_state.py` | Singleton de sesión. Almacena usuario, tokens, rol. Persistencia cifrada | cryptography |
| `role_guard.py` | RBAC. Matriz de permisos por rol. Habilita/deshabilita UI según permisos | user_state |
| `navigation.py` | Navegación entre vistas en QStackedWidget. Historial de navegación | PyQt6 |
| `validators.py` | Validación de RUT, email, contraseña, teléfono | re |
| `errors.py` | Excepciones personalizadas y diálogos de error/éxito | PyQt6 |

### 🖼️ Interfaces de Usuario

| Ventana | Funcionalidad | Permisos Requeridos |
|---------|---------------|---------------------|
| `login_window.py` | Login con usuario/contraseña. Restauración de sesión | Público |
| `register_window.py` | Registro de nuevos usuarios. Estado PENDIENTE | Público |
| `dashboard_window.py` | Dashboard con sidebar y QStackedWidget. Navegación dinámica | Autenticado |
| `inicio_view.py` | Vista de bienvenida con stats | Autenticado |
| `perfil_window.py` | Editar perfil y cambiar contraseña | Autenticado |
| `usuarios_window.py` | Aprobar usuarios, activar/desactivar | Admin |
| `pacientes_window.py` | CRUD de pacientes con búsqueda | view_pacientes |
| `boxes_window.py` | CRUD de boxes | view_boxes |
| `atenciones_window.py` | CRUD de atenciones. Filtra por profesional | view_atenciones |
| `reportes_window.py` | Placeholder de reportes | view_reportes |

### 🔧 Recursos

| Archivo | Contenido |
|---------|-----------|
| `constants.py` | URLs API, roles, estados, configuración UI, endpoints |
| `styles.qss` | Estilos Qt: botones, tablas, inputs, colores corporativos |

### 🛠️ Scripts de Utilidad

| Script | Uso |
|--------|-----|
| `generate_key.py` | Genera clave Fernet para cifrado de sesión |
| `check_setup.py` | Verifica Python, dependencias, .env, estructura |

## 🔐 Flujo de Autenticación

```
┌─────────────┐
│ Login       │
│ Window      │
└──────┬──────┘
       │ credentials
       ▼
┌─────────────┐    POST /auth/login    ┌──────────┐
│   Auth      │─────────────────────────►│ Backend  │
│ Controller  │◄─────────────────────────│ FastAPI  │
└──────┬──────┘    access + refresh     └──────────┘
       │            tokens
       │ set_session()
       ▼
┌─────────────┐
│ User State  │─────► .session.enc (cifrado)
│  (Singleton)│
└──────┬──────┘
       │ emit signal
       ▼
┌─────────────┐
│ Dashboard   │
│   Window    │
└─────────────┘
```

## 🔄 Flujo de Navegación

```
┌──────────────────────────────────────┐
│         Dashboard Window             │
├──────────────┬───────────────────────┤
│   Sidebar    │   Stacked Widget      │
│              │                       │
│  • Inicio    │  ┌─────────────────┐ │
│  • Perfil    │  │  Inicio View    │ │
│  • Usuarios  │  │                 │ │
│  • Pacientes │  │  (active page)  │ │
│  • Boxes     │  │                 │ │
│  • Atenciones│  └─────────────────┘ │
│  • Reportes  │                       │
└──────────────┴───────────────────────┘
       │
       │ on_nav_changed()
       ▼
┌─────────────┐
│ Navigation  │
│ Controller  │
│             │
│ navigate_to()
└─────────────┘
```

## 🎨 Sistema de Permisos (RBAC)

### Matriz de Permisos

| Permiso | Admin | Profesional | Administrativo |
|---------|-------|-------------|----------------|
| `approve_user` | ✅ | ❌ | ❌ |
| `create_paciente` | ✅ | ✅ | ❌ |
| `edit_paciente` | ✅ | ✅ | ❌ |
| `delete_paciente` | ✅ | ❌ | ❌ |
| `view_pacientes` | ✅ | ✅ | ✅ |
| `create_box` | ✅ | ❌ | ❌ |
| `edit_box` | ✅ | ❌ | ❌ |
| `delete_box` | ✅ | ❌ | ❌ |
| `view_boxes` | ✅ | ✅ | ✅ |
| `create_atencion` | ✅ | ✅ | ❌ |
| `edit_atencion` | ✅ | ❌ | ❌ |
| `edit_own_atencion` | ✅ | ✅ | ❌ |
| `view_atenciones` | ✅ | ❌ | ✅ |
| `view_own_atenciones` | ✅ | ✅ | ❌ |
| `view_reportes_generales` | ✅ | ❌ | ❌ |
| `view_reportes` | ✅ | ✅ | ✅ |

### Aplicación de Permisos

```python
# En cualquier ventana
from controllers.role_guard import RoleGuard, Permission

role_guard = RoleGuard()

# Ocultar botón si no tiene permiso
role_guard.guard_button(
    self.create_button,
    Permission.CREATE_PACIENTE,
    hide=True  # Oculta si no tiene permiso
)

# Verificar permiso programáticamente
if role_guard.has_permission(Permission.EDIT_PACIENTE):
    # Permitir edición
    pass
```

## 📊 Flujo de Datos

### Creación de Paciente

```
Usuario → PacientesWindow → PacienteDialog → validate_form()
                                                    │
                                                    ▼
                                              get_data()
                                                    │
                                                    ▼
         api_client.create_paciente(data)
                    │
                    ▼
         POST /pacientes (con JWT header)
                    │
                    ▼
              Backend FastAPI
                    │
                    ▼
           201 Created + paciente
                    │
                    ▼
         load_pacientes() → refresh tabla
```

## 🔒 Seguridad

### Almacenamiento de Tokens

```python
# user_state.py
def save_to_file(self, remember_me: bool):
    data = {
        "access_token": self._access_token,
        "refresh_token": self._refresh_token if remember_me else None,
        ...
    }

    # Cifrado con Fernet (AES-128)
    encrypted = self._cipher.encrypt(json.dumps(data).encode())
    SESSION_FILE.write_bytes(encrypted)
```

### Refresh Automático

```python
# api_client.py
async def _refresh_token_if_needed(self):
    if self.user_state.needs_refresh():
        # Auto-refresh si quedan < 60 segundos
        await self.refresh_token()
```

## 🧪 Testing

### Test Manual de Roles

```bash
# Test 1: Admin puede aprobar usuarios
python main.py
# Login como admin → Usuarios → Aprobar usuario pendiente

# Test 2: Profesional solo ve sus atenciones
python main.py
# Login como profesional → Atenciones → Verificar filtro

# Test 3: Administrativo solo lectura
python main.py
# Login como administrativo → Verificar botones deshabilitados
```

## 📦 Dependencias Clave

| Paquete | Versión | Uso |
|---------|---------|-----|
| PyQt6 | 6.6.1 | Framework GUI |
| qasync | 0.27.1 | Event loop asyncio para Qt |
| httpx | 0.26.0 | Cliente HTTP async |
| cryptography | 41.0.7 | Cifrado Fernet para sesión |
| python-dotenv | 1.0.0 | Variables de entorno |
| pydantic | 2.5.3 | Validación de datos |

## 🔄 Ciclo de Vida de la Aplicación

```
main.py
  │
  ├─► Application()
  │     │
  │     ├─► load_styles()
  │     ├─► show_login()
  │     │     │
  │     │     └─► LoginWindow.try_restore_session()
  │     │           │
  │     │           ├─► ✅ Sesión válida → show_dashboard()
  │     │           └─► ❌ Sin sesión → esperar login
  │     │
  │     └─► run() → QEventLoop
  │
  ├─► Login exitoso
  │     │
  │     └─► DashboardWindow()
  │           │
  │           ├─► setup_navigation()
  │           ├─► apply_role_permissions()
  │           └─► showMaximized()
  │
  └─► Logout
        │
        └─► show_login() (reiniciar ciclo)
```

---

**Última actualización:** 2025
**Versión:** 1.0.0
