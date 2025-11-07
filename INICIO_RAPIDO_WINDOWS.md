# 🚀 Guía de Inicio Rápido - Windows

Esta guía te ayudará a ejecutar el Sistema de Agenda Clínica en Windows con Backend FastAPI y Frontend PyQt6.

## 📁 Estructura del Proyecto

```
Boxes/
├── app/                      # 🔧 Backend FastAPI (código fuente)
│   ├── presentacion/
│   │   └── api_rest/
│   │       └── main.py      # Aplicación FastAPI principal
│   ├── dominio/
│   ├── infraestructura/
│   └── aplicacion/
├── frontend_pyqt/            # 🖥️ Frontend PyQt6 (interfaz gráfica)
│   ├── controllers/
│   ├── ui/
│   ├── resources/
│   └── main.py              # Aplicación PyQt6 principal
├── alembic/                  # 📊 Migraciones de base de datos
├── run_server.bat           # ▶️ Script para ejecutar SOLO el backend
├── run_all.bat              # ⚡ Script para ejecutar Backend + Frontend
└── install_deps.bat         # 📦 Script para instalar dependencias del backend
```

## ⚡ Inicio Rápido (Método Recomendado)

### Opción A: Ejecutar Backend + Frontend Juntos

```batch
run_all.bat
```

Este script:
1. ✅ Inicia el backend FastAPI en puerto 8000
2. ✅ Espera 5 segundos
3. ✅ Inicia el frontend PyQt6
4. ✅ Configura el entorno virtual del frontend si no existe

### Opción B: Ejecutar Solo el Backend

```batch
run_server.bat
```

Luego accede a:
- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs

### Opción C: Ejecutar Solo el Frontend

```batch
cd frontend_pyqt
run_frontend.bat
```

**IMPORTANTE:** El backend debe estar corriendo en http://localhost:8000

---

## 📋 Configuración Inicial (Primera Vez)

### 1. Instalar Poetry (para el backend)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Agregar Poetry al PATH:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","User") + ";$env:APPDATA\Python\Scripts",
  "User"
)
```

### 2. Instalar dependencias del Backend

```batch
install_deps.bat
```

### 3. Configurar base de datos

```batch
setup_db.bat
```

Este script:
- Ejecuta migraciones de Alembic
- Crea datos iniciales (usuarios de prueba)
- Muestra las credenciales de acceso

### 4. Configurar Frontend

```batch
cd frontend_pyqt

REM Crear entorno virtual
python -m venv venv

REM Activar entorno virtual
venv\Scripts\activate.bat

REM Actualizar pip
pip install --upgrade pip

REM Instalar dependencias
pip install -r requirements.txt

REM Copiar archivo de configuración
copy .env.example .env

REM Generar clave de cifrado
python scripts\generate_key.py
```

Edita el archivo `.env` y agrega la clave generada:

```env
API_BASE_URL=http://localhost:8000
ENCRYPTION_KEY=tu-clave-generada-aqui
```

### 5. Verificar configuración del Frontend

```batch
python scripts\check_setup.py
```

---

## 🎯 Ejecutar el Sistema Completo

### Método 1: Script Automático (Recomendado)

```batch
run_all.bat
```

### Método 2: Manual (dos terminales)

**Terminal 1 - Backend:**
```batch
run_server.bat
```

**Terminal 2 - Frontend:**
```batch
cd frontend_pyqt
run_frontend.bat
```

---

## 🔐 Credenciales de Prueba

Después de ejecutar `setup_db.bat`, puedes usar estas credenciales:

### Administrador
- **Email:** admin@clinica.cl
- **Contraseña:** admin123
- **Permisos:** Todos los permisos del sistema

### Recepción
- **Email:** recepcion@clinica.cl
- **Contraseña:** recepcion123
- **Permisos:** Ver y crear pacientes, ver boxes

### Profesional
- **Email:** juan.perez@clinica.cl
- **Contraseña:** prof123
- **Permisos:** Gestionar pacientes, crear atenciones

---

## 🐛 Solución de Problemas

### ❌ Error: "Poetry no está instalado"

**Solución:**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Reinicia PowerShell después de la instalación.

### ❌ Error: "No se puede cargar Activate.ps1"

**Solución:**
Usa `activate.bat` en lugar de `Activate.ps1`:
```batch
venv\Scripts\activate.bat
```

O cambia la política de ejecución de PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Error: "No se encuentra main.py"

**Solución:**
Asegúrate de estar en el directorio correcto:
```batch
REM Para backend:
cd C:\Users\matia\Desktop\Gestion_Box\Boxes

REM Para frontend:
cd C:\Users\matia\Desktop\Gestion_Box\Boxes\frontend_pyqt
```

### ❌ Error: "cannot import name 'QAction' from 'PyQt6.QtWidgets'"

**Solución:**
Este error ya está corregido. Si aparece:
```batch
cd frontend_pyqt
pip install --upgrade PyQt6
```

### ❌ Error: "Error de conexión" en el frontend

**Solución:**
1. Verifica que el backend esté corriendo:
   ```batch
   curl http://localhost:8000/health
   ```

2. Si no está corriendo, ejecútalo:
   ```batch
   run_server.bat
   ```

3. Verifica el archivo `.env` del frontend:
   ```env
   API_BASE_URL=http://localhost:8000
   ```

### ❌ Error: "Usuario no aprobado"

**Solución:**
Los usuarios creados desde el frontend deben ser aprobados por un administrador:

1. Inicia sesión como administrador (admin@clinica.cl)
2. Ve a la sección "Usuarios"
3. Aprueba el usuario pendiente

O usa directamente un usuario de prueba ya aprobado.

---

## 📚 Documentación Adicional

- `README.md` - Documentación completa del proyecto
- `SETUP_WINDOWS.md` - Guía detallada de instalación en Windows
- `ARQUITECTURA_AGENDA_CLINICA.md` - Arquitectura del sistema
- `frontend_pyqt/README.md` - Documentación del frontend
- `frontend_pyqt/QUICKSTART.md` - Guía rápida del frontend

---

## 🔧 Comandos Útiles

### Backend

```batch
REM Instalar/actualizar dependencias
install_deps.bat

REM Configurar/resetear base de datos
setup_db.bat

REM Iniciar servidor
run_server.bat

REM Ejecutar migraciones manualmente
poetry run alembic upgrade head

REM Crear nueva migración
poetry run alembic revision --autogenerate -m "descripcion"
```

### Frontend

```batch
cd frontend_pyqt

REM Verificar configuración
python scripts\check_setup.py

REM Generar nueva clave de cifrado
python scripts\generate_key.py

REM Ejecutar frontend
python main.py

REM O usar el script
run_frontend.bat
```

---

## 🚀 Próximos Pasos

1. ✅ Ejecuta `run_all.bat` para iniciar el sistema
2. ✅ Inicia sesión con un usuario de prueba
3. ✅ Explora las diferentes funcionalidades
4. ✅ Crea boxes, pacientes y atenciones de prueba
5. ✅ Prueba los diferentes roles (Admin, Recepción, Profesional)

---

**¡El sistema está listo para usar! 🎉**

Si encuentras algún problema, consulta la sección "Solución de Problemas" o revisa los logs del backend y frontend.
