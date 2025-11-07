# Guía de Instalación en Windows 11

Esta guía te ayudará a configurar y ejecutar el Sistema de Agenda Clínica en Windows 11 con **Python 3.12**, **Poetry 2.2.1+**, y dependencias optimizadas (passlib 1.7.4 + bcrypt 4.1.2).

## 🚀 Método Rápido: Scripts Batch (RECOMENDADO)

Hemos creado un **script de inicialización automática** que verifica y configura todo por ti, mostrando el progreso en una interfaz gráfica.

### Scripts Disponibles

Se han creado **scripts batch** optimizados que evitan conflictos con Anaconda y otras instalaciones de Python:

1. **`install_deps.bat`** - Instala/actualiza dependencias con Poetry
2. **`setup_db.bat`** - Configura la base de datos (migraciones + seed)
3. **`run_server.bat`** - Inicia el servidor FastAPI con configuración optimizada

### Instalación en 3 pasos

**Paso 1: Instalar dependencias**
```batch
install_deps.bat
```

**Paso 2: Configurar base de datos**
```batch
setup_db.bat
```

**Paso 3: Iniciar servidor**
```batch
run_server.bat
```

O accede a http://localhost:8000/docs

### ¿Qué resuelven estos scripts?

- ✅ **Limpian PYTHONPATH** para evitar conflictos con Anaconda
- ✅ **Fuerzan el uso del venv de Poetry** (`.venv`)
- ✅ **Configuran `--reload-dir ./app`** para recargas correctas
- ✅ **Silencian warnings de passlib/bcrypt** en el logging
- ✅ **Seed idempotente** (no falla si los datos ya existen)

### Si prefieres instalación manual

Si prefieres hacerlo manualmente o los scripts no funcionan, sigue la **Guía de Instalación Manual** a continuación.

---

## 📋 Guía de Instalación Manual

## Requisitos Previos

- **Python 3.12.3 o superior** instalado (verificar con `py -0p` en PowerShell)
- **Poetry 2.2.1 o superior** (gestor de dependencias)
- **PowerShell** o **CMD** (incluido en Windows)
- **Git** para Windows (opcional, para clonar el repositorio)

### Nota importante sobre Anaconda

Si tienes **Anaconda** instalado, los scripts batch incluidos limpian automáticamente el `PYTHONPATH` para evitar conflictos. Asegúrate de usar los scripts `.bat` o sigue las instrucciones de la sección "Evitar conflictos con Anaconda" más abajo.

## Paso 1: Instalar Poetry

Poetry es el gestor de dependencias del proyecto. Para instalarlo:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Después de instalar, agrega Poetry al PATH:

```powershell
# Agregar permanentemente al PATH del usuario
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","User") + ";$env:APPDATA\Python\Scripts",
  "User"
)

# Refrescar PATH de la sesión actual
$env:Path = [Environment]::GetEnvironmentVariable("Path","User") + ";" + [Environment]::GetEnvironmentVariable("Path","Machine")
```

Verifica la instalación:

```powershell
poetry --version
```

## Paso 2: Configurar el Entorno Virtual

Navega al directorio del proyecto y configura Poetry para crear el entorno virtual dentro del proyecto:

```powershell
cd C:\Users\matia\Desktop\Gestion_Box\Boxes

# Configurar Poetry para crear venv en el proyecto
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Usar Python 3.12
poetry env use python3.12
```

Si tienes múltiples versiones de Python (o Anaconda), especifica la ruta completa:

```powershell
# Primero, encuentra la ruta de Python 3.12
py -3.12 -c "import sys; print(sys.executable)"

# Luego usa esa ruta (reemplaza con la ruta que imprimió el comando anterior)
poetry env use "RUTA_DE_PYTHON"

# Ejemplo en Windows:
# poetry env use "C:\Users\matia\AppData\Local\Programs\Python\Python312\python.exe"
```

### Evitar conflictos con Anaconda

Si tienes Anaconda instalado y Poetry intenta usar el intérprete de Anaconda:

```powershell
# Limpiar PYTHONPATH temporalmente
$env:PYTHONPATH = ""

# Verificar que .venv usa el Python correcto
.\.venv\Scripts\python.exe --version
# Debe mostrar: Python 3.12.x

# Si no es correcto, elimina .venv y recréalo
Remove-Item -Recurse -Force .venv
poetry env use python3.12
poetry install --no-root
```

## Paso 3: Instalar Dependencias

```powershell
# Regenerar lock file si es necesario
poetry lock

# Instalar dependencias (sin instalar el paquete raíz)
poetry install --no-root
```

## Paso 4: Configurar Variables de Entorno

Crea el archivo `.env` en la raíz del proyecto con codificación ASCII para evitar problemas:

```powershell
$envText = @"
DATABASE_URL=sqlite:///./agenda_clinica.db
SECRET_KEY=CHANGE-THIS-SECRET-KEY-IN-PRODUCTION
CORS_ORIGINS=["http://localhost:8000","http://127.0.0.1:8000"]
ENABLE_ML_SCORING=false
"@
Set-Content -Path .env -Value $envText -Encoding Ascii
```

### Configuración Completa Recomendada

Para una configuración más completa, puedes copiar el archivo de ejemplo:

```powershell
Copy-Item -Path ".env.example" -Destination ".env" -Force
```

Y luego editarlo con tu editor preferido (asegúrate de guardar con codificación UTF-8 sin BOM o ASCII).

## Paso 5: Inicializar la Base de Datos

```powershell
# Ejecutar migraciones de Alembic
poetry run alembic upgrade head

# Cargar datos iniciales (usuarios de prueba, etc.)
poetry run python -m app.scripts.seed_data
```

## Paso 6: Ejecutar el Servidor

```powershell
# IMPORTANTE: Limpiar PYTHONPATH antes de iniciar (para evitar conflictos con Anaconda)
$env:PYTHONPATH = ""

# Desarrollo (con recarga automática)
# El flag --reload-dir asegura que solo se monitorea la carpeta app/
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir ./app

# Producción (sin recarga)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Recomendación:** Usa el script `run_server.bat` que ya incluye estas configuraciones optimizadas.

El servidor estará disponible en:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

## Solución de Problemas Comunes

### Error: "poetry: El término 'poetry' no se reconoce"

**Solución:** Poetry no está en el PATH. Ejecuta:

```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

### Error: "The currently activated Python version is not supported"

**Solución:** El proyecto requiere Python 3.12+. Instala Python 3.12 o superior y configura Poetry para usarlo:

```powershell
poetry env use python3.12
```

### Error: "pyproject.toml changed significantly since poetry.lock was last generated"

**Solución:** Regenera el archivo lock:

```powershell
Remove-Item .\poetry.lock -Force
poetry lock
poetry install --no-root
```

### Error: "Extra inputs are not permitted" al cargar .env

**Problema:** El archivo `.env` tiene un BOM (Byte Order Mark) o caracteres invisibles.

**Solución:** Recrea el archivo con codificación ASCII:

```powershell
$envText = @"
DATABASE_URL=sqlite:///./agenda_clinica.db
SECRET_KEY=CHANGE-THIS-SECRET-KEY-IN-PRODUCTION
CORS_ORIGINS=["http://localhost:8000","http://127.0.0.1:8000"]
ENABLE_ML_SCORING=false
"@
Set-Content -Path .env -Value $envText -Encoding Ascii
```

### Error: "error reading bcrypt version" (warning de passlib)

**Problema:** Warning conocido entre `passlib 1.7.4` y `bcrypt 4.1.2` al verificar versión.

**Solución:**
- El warning NO afecta la funcionalidad (los hashes funcionan correctamente)
- Ya está silenciado en `app/infraestructura/logging/logger.py`
- Si aún aparece, es solo informativo y puedes ignorarlo

Si quieres asegurar las versiones correctas:

```powershell
poetry lock
poetry install --no-root
```

### Error: "No file/folder found for package agenda-clinica"

**Problema:** Poetry intenta instalar el proyecto como paquete.

**Solución:** Usa siempre `--no-root`:

```powershell
poetry install --no-root
```

### Limpiar Entornos Virtuales Antiguos

Si tienes problemas con entornos virtuales antiguos:

```powershell
# Listar todos los entornos
poetry env list --full-path

# Remover entorno específico
poetry env remove nombre-del-entorno

# O eliminar manualmente la carpeta .venv del proyecto
Remove-Item -Recurse -Force .venv
```

## Comandos Útiles

```powershell
# Ver versión de Poetry
poetry --version

# Ver información del entorno virtual
poetry env info

# Listar todos los entornos virtuales
poetry env list

# Actualizar dependencias
poetry update

# Agregar una nueva dependencia
poetry add nombre-paquete

# Ejecutar tests
poetry run pytest

# Ver cobertura de tests
poetry run pytest --cov=app --cov-report=html

# Formatear código con black
poetry run black app/

# Linting con ruff
poetry run ruff check app/

# Type checking con mypy
poetry run mypy app/
```

## Usuarios de Prueba

Después de ejecutar `seed_data`, tendrás estos usuarios disponibles:

| Email | Contraseña | Rol |
|-------|-----------|-----|
| admin@clinica.cl | admin123 | Administrador |
| recepcion@clinica.cl | recepcion123 | Recepción |
| juan.perez@clinica.cl | prof123 | Profesional (Kinesiólogo) |

## Estructura del Proyecto

```
Boxes/
├── app/                    # Código fuente principal
│   ├── api/               # Endpoints de la API
│   ├── dominio/           # Lógica de negocio
│   ├── infraestructura/   # Base de datos, seguridad
│   ├── schemas/           # Modelos Pydantic
│   ├── scripts/           # Scripts utilitarios
│   └── main.py           # Punto de entrada
├── alembic/               # Migraciones de base de datos
├── tests/                 # Tests automatizados
├── .env                   # Variables de entorno (crear)
├── .env.example          # Ejemplo de variables
├── pyproject.toml        # Configuración de Poetry
└── README.md             # Documentación principal
```

### Error: Uvicorn intenta usar rutas de Anaconda (anaconda3) al hacer reload

**Problema:** Al usar `--reload`, Uvicorn intenta monitorear rutas de `anaconda3` aunque el proyecto usa Poetry.

**Síntomas:**
```
WatchFilesReload detected changes in 'C:\\Users\\..\\anaconda3\\...'
```

**Solución:**

1. **Usar el script `run_server.bat`** (recomendado) - ya limpia el PYTHONPATH automáticamente

2. **O manualmente antes de cada ejecución:**
```powershell
# Limpiar PYTHONPATH
$env:PYTHONPATH = ""

# Verificar que usas el Python correcto
poetry run python -c "import sys; print(sys.executable)"
# Debe mostrar: ...\Boxes\.venv\Scripts\python.exe

# Iniciar con --reload-dir para limitar el monitoreo
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir ./app
```

3. **Solución permanente:** Crear un perfil de PowerShell que limpie PYTHONPATH:
```powershell
# Editar perfil de PowerShell
notepad $PROFILE

# Agregar al final:
$env:PYTHONPATH = ""
```

## 🔧 Checklist de Verificación Final

Antes de reportar un problema, verifica que:

- [ ] Python 3.12.3+ está instalado (`python --version`)
- [ ] Poetry 2.2.1+ está instalado (`poetry --version`)
- [ ] El venv está en `.venv` dentro del proyecto (`poetry env info`)
- [ ] Las dependencias están instaladas (`poetry install --no-root`)
- [ ] El archivo `.env` existe y está correctamente formateado
- [ ] Las migraciones se ejecutaron (`poetry run alembic upgrade head`)
- [ ] Los datos de seed se cargaron (`poetry run python -m app.scripts.seed_data`)
- [ ] `PYTHONPATH` está limpio si usas Anaconda
- [ ] Usas `--reload-dir ./app` con uvicorn

## Próximos Pasos

1. Explora la documentación de la API en http://localhost:8000/docs
2. Lee el archivo `README.md` para más información sobre el proyecto
3. Revisa `CODIGO_BASE.md` para entender la arquitectura
4. Consulta `CONFIGURACION_DESPLIEGUE.md` para desplegar en producción

## Soporte

Si encuentras problemas adicionales:

1. Verifica que todos los pasos del checklist anterior están completos
2. Revisa los logs de error para más detalles
3. Asegúrate de tener la versión correcta de Python (3.12.3+)
4. Verifica que el archivo `.env` está en formato correcto (ASCII o UTF-8 sin BOM)
5. Si usas Anaconda, asegúrate de limpiar `PYTHONPATH` antes de ejecutar comandos
