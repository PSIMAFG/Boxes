# Guía de Instalación en Windows

Esta guía te ayudará a configurar y ejecutar el Sistema de Agenda Clínica en Windows.

## Requisitos Previos

- **Python 3.11 o superior** instalado (verificar con `py -0p` en PowerShell)
- **PowerShell** (incluido en Windows)
- **Git** para Windows (opcional, para clonar el repositorio)

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
cd C:\Users\TU_USUARIO\Desktop\Gestion_Box\Boxes

# Configurar Poetry para crear venv en el proyecto
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Usar Python 3.11 o superior
poetry env use python3.11
```

Si tienes múltiples versiones de Python, especifica la ruta completa:

```powershell
# Primero, encuentra la ruta de Python 3.11+
py -3.11 -c "import sys; print(sys.executable)"

# Luego usa esa ruta (reemplaza con la ruta que imprimió el comando anterior)
poetry env use "RUTA_DE_PYTHON"
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

### Primera Instalación (Base de Datos Limpia)

```powershell
# Ejecutar migraciones de Alembic
poetry run alembic upgrade head

# Cargar datos iniciales (usuarios de prueba, etc.)
poetry run python -m app.scripts.seed_data
```

### Si Ya Existe una Base de Datos (Reinstalación)

Si recibes un error como `table usuarios already exists`, necesitas limpiar la base de datos:

**Opción 1: Eliminar la base de datos y empezar de nuevo (Recomendado para desarrollo)**

```powershell
# Eliminar archivo de base de datos SQLite
Remove-Item .\agenda_clinica.db -Force -ErrorAction SilentlyContinue

# Ejecutar migraciones desde cero
poetry run alembic upgrade head

# Cargar datos iniciales
poetry run python -m app.scripts.seed_data
```

**Opción 2: Revertir migraciones y reaplicarlas**

```powershell
# Revertir todas las migraciones
poetry run alembic downgrade base

# Aplicar migraciones nuevamente
poetry run alembic upgrade head

# Cargar datos iniciales
poetry run python -m app.scripts.seed_data
```

## Paso 6: Ejecutar el Servidor

```powershell
# Desarrollo (con recarga automática)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción (sin recarga)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

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

**Solución:** El proyecto requiere Python 3.11+. Instala Python 3.11 o superior y configura Poetry para usarlo:

```powershell
poetry env use python3.11
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

### Error: "bcrypt version" o "password cannot be longer than 72 bytes"

**Problema:** Incompatibilidad entre `passlib` y `bcrypt 5.x`.

**Solución:** Ya está resuelto en el `pyproject.toml`. Si persiste:

```powershell
poetry lock
poetry install --no-root
```

### Error: "No file/folder found for package agenda-clinica"

**Problema:** Poetry intenta instalar el proyecto como paquete.

**Solución:** Ya está resuelto con `package-mode = false` en `pyproject.toml`. Si persiste, usa `--no-root`:

```powershell
poetry install --no-root
```

### Error: "table usuarios already exists" al ejecutar alembic

**Problema:** La base de datos ya tiene tablas de un intento previo de instalación.

**Solución:** Elimina la base de datos y vuelve a crearla:

```powershell
Remove-Item .\agenda_clinica.db -Force -ErrorAction SilentlyContinue
poetry run alembic upgrade head
poetry run python -m app.scripts.seed_data
```

### Error: "Could not import module app.main" al ejecutar uvicorn

**Problema:** Ya resuelto. El archivo `app/main.py` faltaba.

**Solución:** Después de hacer pull de los últimos cambios, el archivo `app/main.py` estará presente. Si persiste, verifica que el módulo se puede importar:

```powershell
poetry run python -c "from app.main import app; print('OK')"
```

### Error: "ValueError: RUT inválido" al ejecutar seed_data

**Problema:** Ya resuelto. Los RUTs en el script de seed_data estaban mal calculados.

**Solución:** Después de hacer pull de los últimos cambios, los RUTs serán válidos. Los RUTs de prueba son:
- `12345678-5` (Pedro Sánchez)
- `16432341-4` (Ana Martínez)
- `18765432-3` (Carlos López)

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

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| doctor1 | doctor123 | Doctor |
| recep1 | recep123 | Recepcionista |

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

## Próximos Pasos

1. Explora la documentación de la API en http://localhost:8000/docs
2. Lee el archivo `README.md` para más información sobre el proyecto
3. Revisa `CODIGO_BASE.md` para entender la arquitectura
4. Consulta `CONFIGURACION_DESPLIEGUE.md` para desplegar en producción

## Soporte

Si encuentras problemas adicionales:

1. Verifica que todos los pasos anteriores se completaron correctamente
2. Revisa los logs de error para más detalles
3. Asegúrate de tener la versión correcta de Python (3.11+)
4. Verifica que el archivo `.env` está en formato correcto (ASCII o UTF-8 sin BOM)
