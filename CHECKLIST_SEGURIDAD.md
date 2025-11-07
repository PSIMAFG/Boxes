# 🔒 CHECKLIST DE SEGURIDAD COMPLETO

**Sistema:** Agenda Clínica
**Fecha:** 2025-11-07

---

## [13] AUTENTICACIÓN Y AUTORIZACIÓN

### ✅ Autenticación

- [ ] **Contraseñas seguras:**
  - Mínimo 8 caracteres
  - Al menos 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
  - Validación en backend y frontend

- [ ] **Hashing de contraseñas:**
  - Usar bcrypt con factor de costo >= 12
  - NUNCA almacenar contraseñas en texto plano
  - NUNCA retornar password_hash en respuestas

- [ ] **JWT Tokens:**
  - Access token: duración corta (15 minutos)
  - Refresh token: duración media (7 días)
  - Usar claves secretas diferentes para access y refresh tokens
  - SECRET_KEY mínimo 32 caracteres aleatorios
  - Algoritmo: HS256 o RS256
  - Claims mínimos: user_id, email, rol, exp, iat

- [ ] **Refresh Tokens:**
  - Almacenar hash del refresh token en BD (no el token raw)
  - Implementar revocación manual
  - Detectar reutilización de tokens (token family)
  - Limpiar tokens expirados periódicamente

- [ ] **Flujo de registro:**
  - Usuario registrado queda en estado PENDIENTE
  - Admin aprueba y asigna rol
  - Validar email único
  - Confirmación por email (opcional pero recomendado)

---

### ✅ Autorización (RBAC)

- [ ] **Control de acceso basado en roles:**
  - Implementar RequiereAdmin, RequiereProfesional, RequiereAdministrativo
  - Validar rol en CADA endpoint protegido
  - No confiar en el frontend para validación de permisos

- [ ] **Matriz de permisos:**
  - Admin: acceso total
  - Profesional: crear pacientes (demográfico), registrar atenciones propias
  - Administrativo: solo lectura

- [ ] **Validación de propiedad:**
  - Profesional solo puede ver/editar sus propias atenciones
  - Verificar ownership en backend (no solo por rol)

- [ ] **Guards en frontend:**
  - PrivateRoute: requiere autenticación
  - RoleGuard: requiere rol específico
  - Ocultar elementos UI según permisos

---

## [14] VALIDACIÓN Y SANITIZACIÓN

### ✅ Validación de Entrada

- [ ] **Pydantic en Backend:**
  - Usar DTOs con Pydantic para TODAS las entradas
  - Validar tipos, longitudes, formatos
  - Usar EmailStr para emails
  - Validar UUIDs con UUID4

- [ ] **Validaciones de negocio:**
  - RUT válido (dígito verificador)
  - Fechas lógicas (fecha_nacimiento < hoy)
  - Rangos válidos (nivel_apoyo 1-3, piso 1-2)

- [ ] **Sanitización:**
  - Escapar HTML en inputs de texto libre
  - NO ejecutar código dinámico desde inputs
  - Limitar tamaño de payloads (FastAPI max_body_size)

---

### ✅ Inyección SQL

- [ ] **SQLAlchemy ORM:**
  - SIEMPRE usar ORM, NUNCA queries raw
  - Si se requiere raw SQL, usar parámetros preparados
  - Ejemplo: `session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})`

- [ ] **No interpolar strings:**
  - ❌ NUNCA: `f"SELECT * FROM users WHERE email = '{email}'"`
  - ✅ USAR: ORM con filtros

---

## [15] SEGURIDAD DE API

### ✅ CORS

- [ ] **Configuración CORS:**
  - Definir orígenes permitidos específicos (NO usar "*" en producción)
  - Ejemplo: `["https://clinica.ejemplo.com", "https://app.clinica.com"]`
  - allow_credentials=True para cookies

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clinica.ejemplo.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### ✅ Rate Limiting

- [ ] **Limitar requests:**
  - Usar slowapi o similar
  - Límites sugeridos:
    - Login: 5 intentos por minuto por IP
    - Registro: 3 intentos por hora por IP
    - API general: 100 requests/minuto por usuario

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
def login(...):
    pass
```

---

### ✅ Headers de Seguridad

- [ ] **Headers HTTP:**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy`: definir política estricta

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Redirigir HTTP -> HTTPS en producción
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["clinica.ejemplo.com"])
```

---

### ✅ HTTPS

- [ ] **Certificados SSL:**
  - Usar HTTPS en producción (Let's Encrypt gratuito)
  - NUNCA enviar tokens por HTTP
  - Configurar HSTS

---

## [16] PROTECCIÓN CONTRA ATAQUES

### ✅ XSS (Cross-Site Scripting)

- [ ] **Escapar salidas:**
  - React escapa automáticamente
  - NO usar `dangerouslySetInnerHTML` sin sanitizar
  - Sanitizar HTML con DOMPurify si es necesario

- [ ] **Content Security Policy:**
  - Definir CSP header estricto
  - Bloquear inline scripts

---

### ✅ CSRF (Cross-Site Request Forgery)

- [ ] **Tokens CSRF:**
  - Si usas cookies para auth, implementar CSRF tokens
  - O usar Authorization header (Bearer token) que no se envía automáticamente

- [ ] **SameSite cookies:**
  - Si usas cookies: `SameSite=Strict` o `Lax`

---

### ✅ Clickjacking

- [ ] **X-Frame-Options:**
  - Header: `X-Frame-Options: DENY`
  - O usar CSP: `frame-ancestors 'none'`

---

### ✅ Mass Assignment

- [ ] **DTOs específicos:**
  - NO permitir actualización de campos sensibles desde el frontend
  - Ejemplo: user no puede cambiar su rol directamente
  - Usar DTOs separados para Create, Update, Response

---

### ✅ Information Disclosure

- [ ] **Mensajes de error:**
  - NO exponer stacktraces en producción
  - Mensajes genéricos: "Error interno del servidor"
  - Loggear errores detallados solo en server

- [ ] **Respuestas HTTP:**
  - NO retornar password_hash, tokens internos
  - Usar DTOs de respuesta para controlar qué se expone

---

## [17] AUDITORÍA Y LOGGING

### ✅ Auditoría de Eventos

- [ ] **Registrar eventos críticos:**
  - Login exitoso/fallido
  - Registro de usuario
  - Aprobación de usuario
  - Creación/edición de pacientes
  - Registro de atenciones
  - Cambios de permisos

- [ ] **Datos de auditoría:**
  - usuario_id
  - evento
  - timestamp
  - ip_origen
  - detalles (JSON)

```python
auditoria_repo.registrar(
    usuario_id=usuario.id,
    evento="LOGIN_EXITOSO",
    detalles={"token_family": token_family},
    ip_origen=request.client.host
)
```

---

### ✅ Logging

- [ ] **Logs estructurados:**
  - Usar logging de Python
  - Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - NO loggear contraseñas, tokens, datos sensibles

- [ ] **Rotación de logs:**
  - Implementar rotación por tamaño o fecha
  - Almacenar logs en ubicación segura

---

## [18] BASE DE DATOS

### ✅ Seguridad de BD

- [ ] **Credenciales:**
  - Usuario BD con permisos mínimos necesarios
  - NO usar usuario root/postgres
  - Password fuerte para BD

- [ ] **Connection String:**
  - NUNCA hardcodear en código
  - Usar variables de entorno (.env)
  - .env en .gitignore

- [ ] **Backups:**
  - Backups automáticos diarios
  - Encriptar backups
  - Probar restauración periódicamente

- [ ] **Migraciones:**
  - Usar Alembic
  - Versionar migraciones en git
  - Probar migraciones en staging antes de producción

---

## [19] VARIABLES DE ENTORNO

### ✅ Secrets Management

- [ ] **Variables sensibles en .env:**
  - SECRET_KEY
  - REFRESH_SECRET_KEY
  - DATABASE_URL
  - EMAIL_PASSWORD
  - API_KEYS de terceros

- [ ] **.env.example:**
  - Crear .env.example con variables sin valores
  - Documentar cada variable

- [ ] **.gitignore:**
  - Asegurar que .env está en .gitignore
  - NUNCA commitear secrets

---

## [20] FRONTEND

### ✅ Almacenamiento de Tokens

- [ ] **localStorage vs sessionStorage vs cookies:**
  - ✅ localStorage: access_token, refresh_token (aceptable)
  - ✅ HttpOnly Cookies: refresh_token (más seguro)
  - ❌ NO almacenar en localStorage si hay riesgo XSS alto

- [ ] **Limpiar tokens:**
  - Al logout
  - Al detectar error 401 en refresh

---

### ✅ Validación Frontend

- [ ] **Validación en tiempo real:**
  - Validar inputs antes de submit
  - Mensajes de error claros

- [ ] **NO confiar solo en frontend:**
  - Backend SIEMPRE valida
  - Frontend es solo UX

---

## [21] DEPLOYMENT

### ✅ Producción

- [ ] **Environment:**
  - DEBUG=False
  - CORS origins específicos
  - HTTPS obligatorio

- [ ] **Docker:**
  - Usar imágenes oficiales
  - Escanear vulnerabilidades (docker scan, trivy)
  - NO correr como root

- [ ] **Firewall:**
  - Solo puertos necesarios abiertos (80, 443, 5432 solo interno)
  - BD no accesible desde internet

- [ ] **Actualizaciones:**
  - Mantener dependencias actualizadas
  - Revisar CVEs periódicamente
  - `pip-audit` para Python
  - `npm audit` para Node

---

## [22] TESTING DE SEGURIDAD

### ✅ Pruebas

- [ ] **Tests unitarios:**
  - Validar RBAC
  - Validar validaciones de DTOs
  - Validar hashing de passwords

- [ ] **Tests de integración:**
  - Intentar acceder a endpoints sin token
  - Intentar acceder con rol incorrecto
  - Validar refresh token flow

- [ ] **Penetration Testing:**
  - SQL Injection
  - XSS
  - CSRF
  - Broken Authentication

---

## [23] COMPLIANCE (Si aplica)

### ✅ HIPAA / RGPD

- [ ] **Datos sensibles:**
  - Encriptar datos en tránsito (HTTPS)
  - Encriptar datos en reposo (DB encryption)
  - Derecho al olvido (soft delete)

- [ ] **Consentimiento:**
  - Consentimiento informado para tratamiento de datos
  - Política de privacidad
  - Términos y condiciones

---

## 📋 RESUMEN DE PRIORIDADES

### 🔴 CRÍTICO (Hacer antes de producción)
1. ✅ HTTPS con certificado válido
2. ✅ Contraseñas hasheadas con bcrypt
3. ✅ JWT con SECRET_KEY fuerte
4. ✅ RBAC en todos los endpoints
5. ✅ Validación Pydantic en todas las entradas
6. ✅ CORS configurado correctamente
7. ✅ .env en .gitignore
8. ✅ Auditoría de eventos críticos

### 🟡 IMPORTANTE (Hacer pronto)
1. ✅ Rate limiting en login y registro
2. ✅ Headers de seguridad HTTP
3. ✅ Refresh token con revocación
4. ✅ Logging estructurado
5. ✅ Backups automáticos
6. ✅ Tests de seguridad básicos

### 🟢 RECOMENDADO (Mejoras continuas)
1. ✅ Confirmación de email en registro
2. ✅ 2FA (autenticación de dos factores)
3. ✅ Monitoreo de seguridad (SIEM)
4. ✅ Penetration testing periódico
5. ✅ Escaneo de vulnerabilidades en dependencias
6. ✅ WAF (Web Application Firewall)

---

✅ **Checklist de seguridad completo**
