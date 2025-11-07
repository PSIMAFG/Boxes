# 🚀 Guía de Inicio Rápido

## ⚡ Configuración en 5 Pasos

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Generar clave de cifrado
python scripts/generate_key.py

# Copiar la clave generada al archivo .env
```

### 3️⃣ Editar archivo .env

```env
API_BASE_URL=http://localhost:8000
ENCRYPTION_KEY=tu-clave-generada
```

### 4️⃣ Verificar configuración

```bash
python scripts/check_setup.py
```

### 5️⃣ Ejecutar aplicación

```bash
python main.py
```

---

## 📝 Primer Login

### Opción A: Usuario existente

Si ya tienes un usuario aprobado en el backend:

1. Ingresar usuario y contraseña
2. Marcar "Recordar sesión" (opcional)
3. Clic en "Iniciar Sesión"

### Opción B: Crear nuevo usuario

1. Clic en "Regístrate"
2. Completar formulario:
   - **Nombre completo:** Juan Pérez
   - **RUT:** 12.345.678-9
   - **Email:** juan@ejemplo.com
   - **Usuario:** jperez
   - **Contraseña:** MiPass123
   - **Rol:** Profesional
3. Clic en "Registrarse"
4. **Importante:** El usuario debe ser aprobado por un administrador

### Opción C: Usar usuarios de prueba

Si ejecutaste el script `setup_db.bat` en la raíz del proyecto, ya tienes usuarios creados:

```
Admin:
  Email: admin@clinica.cl
  Password: admin123

Recepción:
  Email: recepcion@clinica.cl
  Password: recepcion123

Profesional:
  Email: juan.perez@clinica.cl
  Password: prof123
```

---

## 🎯 Funcionalidades por Rol

### 👑 Administrador
- ✅ Aprobar/rechazar usuarios nuevos
- ✅ Gestionar boxes (crear, editar, eliminar)
- ✅ Gestionar pacientes completo
- ✅ Ver todas las atenciones
- ✅ Acceso a reportes generales

### 👨‍⚕️ Profesional
- ✅ Crear y editar pacientes
- ✅ Crear y gestionar sus atenciones
- ✅ Ver boxes disponibles
- ✅ Reportes personales

### 📋 Administrativo
- ✅ Ver pacientes (solo lectura)
- ✅ Ver boxes (solo lectura)
- ✅ Ver atenciones (solo lectura)
- ✅ Consultar reportes básicos

---

## 🧪 Pruebas Rápidas

### Test de Login
```bash
python main.py
# Ingresar credenciales válidas
# Verificar que abre el dashboard
```

### Test de CRUD Pacientes
```bash
# 1. Login como Profesional o Admin
# 2. Ir a "Pacientes"
# 3. Clic en "➕ Nuevo Paciente"
# 4. Completar: Juan Pérez, 12.345.678-9, juan@email.com
# 5. Guardar y verificar en la lista
```

### Test de Roles
```bash
# 1. Login como Administrativo
# 2. Verificar que botones de crear/editar están ocultos
# 3. Logout
# 4. Login como Admin
# 5. Verificar que tiene todos los permisos
```

---

## 🐛 Problemas Comunes

### ❌ "No se puede conectar al servidor"

**Solución:**
```bash
# Verificar que el backend esté corriendo
# Desde el directorio raíz del proyecto (Boxes/)
run_server.bat

# O manualmente:
poetry run uvicorn app.main:app --reload
```

### ❌ "Usuario no aprobado"

**Solución:**
- El usuario debe estar en estado APROBADO
- Contactar a un administrador
- O crear un admin desde el backend

### ❌ "Error de importación PyQt6"

**Solución:**
```bash
pip install PyQt6 qasync
```

### ❌ "Invalid encryption key"

**Solución:**
```bash
python scripts/generate_key.py
# Copiar la nueva clave al .env
```

---

## 📞 Ayuda

Para más información, consultar:
- `README.md` - Documentación completa
- `scripts/check_setup.py` - Verificar configuración
- Backend en `http://localhost:8000/docs` - API docs

---

**¡Listo para empezar! 🎉**
