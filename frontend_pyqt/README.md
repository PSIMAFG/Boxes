# 🏥 Sistema de Agenda Clínica - Frontend PyQt6

Frontend de escritorio desarrollado en Python con PyQt6 para el Sistema de Gestión de Agenda Clínica.

## 📋 Características

- ✅ **Autenticación JWT** con refresh token automático
- ✅ **Control de acceso basado en roles** (RBAC)
- ✅ **Persistencia segura de sesión** con cifrado Fernet
- ✅ **Interfaz moderna y responsiva** con PyQt6
- ✅ **Gestión completa** de Pacientes, Boxes y Atenciones
- ✅ **Dashboard dinámico** según rol del usuario
- ✅ **Validaciones robustas** (RUT chileno, email, contraseña)

## 🔧 Requisitos Previos

- Python 3.9 o superior
- Backend FastAPI ejecutándose (por defecto en `http://localhost:8000`)

## 📦 Instalación

### 1. Clonar el repositorio

```bash
cd frontend_pyqt
```

### 2. Crear entorno virtual (recomendado)

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp .env.example .env
```

Editar `.env` y configurar:

```env
# URL del backend (ajustar si es diferente)
API_BASE_URL=http://localhost:8000

# Generar una clave de cifrado única
# Ejecutar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=tu-clave-generada-aqui
```

#### Generar clave de cifrado:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copiar la salida al archivo `.env` en la variable `ENCRYPTION_KEY`.

## 🚀 Ejecución

### Iniciar la aplicación

```bash
python main.py
```

La ventana de login se abrirá automáticamente.

### Primer uso

1. **Registrar un usuario:**
   - En la ventana de login, hacer clic en "Regístrate"
   - Completar el formulario con:
     - Nombre completo
     - RUT chileno válido
     - Email
     - Usuario (mínimo 3 caracteres)
     - Contraseña (mínimo 8 caracteres, con mayúsculas, minúsculas y números)
     - Seleccionar rol: Profesional o Administrativo
   - El usuario quedará en estado PENDIENTE

2. **Aprobar usuario (requiere admin):**
   - Iniciar sesión con usuario administrador
   - Ir a sección "Usuarios"
   - Aprobar el usuario creado

3. **Iniciar sesión:**
   - Usuario y contraseña del usuario aprobado
   - Marcar "Recordar sesión" para persistencia

## 👥 Roles y Permisos

### Administrador (admin)
- ✅ Gestión completa de usuarios (aprobar, activar/desactivar)
- ✅ CRUD completo de pacientes, boxes y atenciones
- ✅ Acceso a todos los reportes
- ✅ Configuración del sistema

### Profesional (profesional)
- ✅ Gestión de pacientes (crear, editar)
- ✅ Vista de boxes (solo lectura)
- ✅ CRUD de sus propias atenciones
- ✅ Reportes personales

### Administrativo (administrativo)
- ✅ Vista de pacientes (solo lectura)
- ✅ Vista de boxes (solo lectura)
- ✅ Vista de atenciones (solo lectura)
- ✅ Reportes básicos

## 🗂️ Estructura del Proyecto

```
frontend_pyqt/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── .env                   # Configuración
├── .env.example           # Ejemplo de configuración
│
├── controllers/           # Lógica de negocio
│   ├── api_client.py     # Cliente HTTP con JWT
│   ├── auth_controller.py # Controlador de autenticación
│   ├── user_state.py     # Gestión de sesión
│   ├── role_guard.py     # Control de acceso RBAC
│   ├── navigation.py     # Sistema de navegación
│   ├── validators.py     # Validadores de campos
│   └── errors.py         # Manejo de errores
│
├── ui/                    # Interfaz de usuario
│   ├── login_window.py   # Ventana de login
│   ├── register_window.py # Ventana de registro
│   ├── dashboard_window.py # Dashboard principal
│   ├── inicio_view.py    # Vista de inicio
│   ├── perfil_window.py  # Ventana de perfil
│   ├── usuarios_window.py # Gestión de usuarios
│   ├── pacientes_window.py # Gestión de pacientes
│   ├── boxes_window.py   # Gestión de boxes
│   ├── atenciones_window.py # Gestión de atenciones
│   └── reportes_window.py # Reportes
│
└── resources/            # Recursos
    ├── constants.py      # Constantes globales
    └── styles.qss        # Estilos Qt
```

## 🔐 Seguridad

### Tokens JWT
- **Access Token:** 15 minutos de validez
- **Refresh Token:** 7 días de validez
- Refresh automático antes de expiración

### Persistencia de Sesión
- Cifrado con **Fernet** (cryptography)
- Almacenamiento local en `.session.enc`
- Nunca almacena contraseñas

### Validaciones
- **RUT chileno** con verificación de dígito
- **Contraseñas robustas** (8+ caracteres, mayúsculas, minúsculas, números)
- **Emails** con formato válido
- **Sanitización** de entradas

## 🧪 Pruebas de Funcionamiento

### Test 1: Login y Navegación

```bash
# 1. Ejecutar aplicación
python main.py

# 2. Iniciar sesión con credenciales válidas
#    (debe tener usuario aprobado en el backend)

# 3. Verificar que se abre el dashboard
# 4. Navegar entre secciones según rol
```

### Test 2: Gestión de Pacientes

```bash
# 1. Iniciar sesión como Profesional o Admin
# 2. Ir a sección "Pacientes"
# 3. Hacer clic en "➕ Nuevo Paciente"
# 4. Completar formulario con datos válidos
# 5. Verificar que se crea correctamente
# 6. Editar el paciente creado
# 7. Verificar actualización
```

### Test 3: Control de Roles

```bash
# 1. Iniciar sesión como Administrativo
# 2. Verificar que solo tiene acceso de lectura
# 3. Los botones de crear/editar/eliminar deben estar ocultos
# 4. Cerrar sesión
# 5. Iniciar como Admin
# 6. Verificar que tiene acceso completo
```

### Test 4: Persistencia de Sesión

```bash
# 1. Iniciar sesión con "Recordar sesión" marcado
# 2. Cerrar la aplicación
# 3. Abrir nuevamente
# 4. Debe restaurar la sesión automáticamente
```

## 🐛 Solución de Problemas

### Error: "No module named 'PyQt6'"

```bash
pip install PyQt6
```

### Error: "Connection refused" al iniciar sesión

Verificar que el backend FastAPI esté ejecutándose:

```bash
# En el directorio del backend
uvicorn main:app --reload
```

### Error: "Invalid encryption key"

Generar una nueva clave de cifrado:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Y actualizar en `.env`.

### La aplicación no carga estilos

Verificar que existe el archivo `resources/styles.qss` en el directorio del proyecto.

## 📝 Usuarios de Prueba

### Crear usuario Admin inicial (Backend)

El usuario administrador inicial debe crearse directamente en el backend:

```python
# En backend, ejecutar script de inicialización
python scripts/create_admin.py
```

O crear manualmente en la base de datos con:
- `role = "admin"`
- `estado = "APROBADO"`
- `is_active = True`

## 🔄 Actualización

Para actualizar dependencias:

```bash
pip install --upgrade -r requirements.txt
```

## 📚 Documentación Adicional

### Endpoints del Backend

El frontend consume los siguientes endpoints del backend:

- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario
- `POST /auth/refresh` - Refrescar token
- `GET /auth/me` - Usuario actual
- `GET /usuarios` - Listar usuarios
- `GET /pacientes` - Listar pacientes
- `POST /pacientes` - Crear paciente
- `GET /boxes` - Listar boxes
- `GET /atenciones` - Listar atenciones
- `POST /admin/users/{id}/approve` - Aprobar usuario (admin)

### Códigos de Estado HTTP

- `200` - Éxito
- `201` - Creado
- `401` - No autenticado
- `403` - Sin permisos
- `404` - No encontrado
- `422` - Error de validación
- `500` - Error del servidor

## 🤝 Contribución

Para contribuir al proyecto:

1. Seguir la estructura de carpetas establecida
2. Usar type hints en Python
3. Documentar funciones con docstrings
4. Respetar el sistema RBAC
5. Validar todos los inputs del usuario

## 📄 Licencia

Este proyecto es parte del Sistema de Agenda Clínica desarrollado para PSIMAFG.

## 👨‍💻 Soporte

Para problemas o consultas, contactar al equipo de desarrollo.

---

**Versión:** 1.0.0
**Última actualización:** 2025
