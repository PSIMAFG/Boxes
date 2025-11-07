# 🐍 EJEMPLOS DE CÓDIGO BACKEND

**Framework:** FastAPI + SQLAlchemy + Pydantic
**Seguridad:** JWT + bcrypt + RBAC

---

## [3] MODELOS Y MIGRACIONES

### 3.1 Modelo de Usuario Sistema (Actualizado)

```python
# app/infraestructura/db/models.py

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum


class EstadoUsuario(enum.Enum):
    """Estados de usuario del sistema"""
    PENDIENTE = "pendiente"  # Esperando aprobación
    ACTIVO = "activo"        # Aprobado y activo
    INACTIVO = "inactivo"    # Desactivado


class RolUsuario(enum.Enum):
    """Roles de usuario del sistema"""
    ADMIN = "admin"
    PROFESIONAL = "profesional"
    ADMINISTRATIVO = "administrativo"  # Actualizado: era "recepcion"


class UsuarioSistemaModel(Base):
    """Usuario autenticado del sistema"""
    __tablename__ = "usuarios_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(255), nullable=False)  # Nuevo campo

    rol = Column(SQLEnum(RolUsuario), nullable=True)  # NULL hasta aprobación
    estado = Column(
        SQLEnum(EstadoUsuario),
        default=EstadoUsuario.PENDIENTE,
        nullable=False,
        index=True
    )

    profesional_id = Column(UUID(as_uuid=True), ForeignKey("profesionales.id"), nullable=True)

    # Auditoría
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    aprobado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=True)
    aprobado_en = Column(DateTime, nullable=True)
    ultimo_login = Column(DateTime, nullable=True)

    # Relaciones
    profesional = relationship("ProfesionalModel")
    aprobador = relationship("UsuarioSistemaModel", remote_side=[id])


class RefreshTokenModel(Base):
    """Refresh tokens para renovación de sesión"""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios_sistema.id"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)  # Hash del refresh token
    token_family = Column(String(100), nullable=False)  # Para detectar reutilización

    revocado = Column(Boolean, default=False, nullable=False, index=True)
    expira_en = Column(DateTime, nullable=False, index=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    usuario = relationship("UsuarioSistemaModel")
```

---

### 3.2 Migración Alembic (Nueva)

```python
# alembic/versions/20250108_add_refresh_tokens.py

"""Add refresh tokens and user approval flow

Revision ID: 20250108_refresh_tokens
Revises: 20250107_box_enhancements
Create Date: 2025-01-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250108_refresh_tokens'
down_revision = '20250107_box_enhancements'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Agregar estado a usuarios_sistema
    op.add_column('usuarios_sistema',
        sa.Column('estado',
            sa.Enum('PENDIENTE', 'ACTIVO', 'INACTIVO', name='estadousuario'),
            nullable=False,
            server_default='ACTIVO'
        )
    )

    # 2. Agregar nombre_completo
    op.add_column('usuarios_sistema',
        sa.Column('nombre_completo', sa.String(255), nullable=False, server_default='')
    )

    # 3. Hacer rol nullable (hasta aprobación)
    op.alter_column('usuarios_sistema', 'rol', nullable=True)

    # 4. Agregar campos de aprobación
    op.add_column('usuarios_sistema',
        sa.Column('aprobado_por', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column('usuarios_sistema',
        sa.Column('aprobado_en', sa.DateTime(), nullable=True)
    )
    op.add_column('usuarios_sistema',
        sa.Column('ultimo_login', sa.DateTime(), nullable=True)
    )

    # 5. Agregar FK para aprobador
    op.create_foreign_key(
        'fk_usuarios_sistema_aprobado_por',
        'usuarios_sistema', 'usuarios_sistema',
        ['aprobado_por'], ['id']
    )

    # 6. Crear tabla refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('token_family', sa.String(100), nullable=False),
        sa.Column('revocado', sa.Boolean(), default=False, nullable=False),
        sa.Column('expira_en', sa.DateTime(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios_sistema.id']),
    )

    # 7. Índices para refresh_tokens
    op.create_index('ix_refresh_tokens_usuario_id', 'refresh_tokens', ['usuario_id'])
    op.create_index('ix_refresh_tokens_revocado', 'refresh_tokens', ['revocado'])
    op.create_index('ix_refresh_tokens_expira_en', 'refresh_tokens', ['expira_en'])


def downgrade():
    op.drop_table('refresh_tokens')
    op.drop_constraint('fk_usuarios_sistema_aprobado_por', 'usuarios_sistema')
    op.drop_column('usuarios_sistema', 'ultimo_login')
    op.drop_column('usuarios_sistema', 'aprobado_en')
    op.drop_column('usuarios_sistema', 'aprobado_por')
    op.alter_column('usuarios_sistema', 'rol', nullable=False)
    op.drop_column('usuarios_sistema', 'nombre_completo')
    op.drop_column('usuarios_sistema', 'estado')
    op.execute("DROP TYPE estadousuario")
```

---

## [4] DTOs (Data Transfer Objects)

### 4.1 DTOs de Autenticación

```python
# app/aplicacion/dtos/auth_dto.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class RegistroRequestDTO(BaseModel):
    """DTO para registro público de usuario"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nombre_completo: str = Field(..., min_length=3, max_length=255)

    @validator('password')
    def validar_password_fuerte(cls, v):
        """Validar que la contraseña sea fuerte"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@clinica.cl",
                "password": "MiPassword123!",
                "nombre_completo": "Juan Pérez González"
            }
        }


class LoginRequestDTO(BaseModel):
    """DTO para login"""
    email: EmailStr
    password: str


class LoginResponseDTO(BaseModel):
    """DTO de respuesta exitosa de login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos hasta expiración
    user: "UsuarioSistemaResponseDTO"


class RefreshTokenRequestDTO(BaseModel):
    """DTO para solicitar nuevo access token"""
    refresh_token: str


class AprobarUsuarioDTO(BaseModel):
    """DTO para aprobar usuario pendiente"""
    rol: str = Field(..., pattern="^(admin|profesional|administrativo)$")
    profesional_id: Optional[str] = None  # UUID del profesional si rol=profesional

    @validator('profesional_id')
    def validar_profesional_id(cls, v, values):
        """Si rol es profesional, profesional_id es obligatorio"""
        if values.get('rol') == 'profesional' and not v:
            raise ValueError('profesional_id es obligatorio para rol profesional')
        return v


class UsuarioSistemaResponseDTO(BaseModel):
    """DTO de respuesta de usuario sistema"""
    id: str
    email: str
    nombre_completo: str
    rol: Optional[str]
    estado: str
    profesional_id: Optional[str]
    creado_en: datetime
    ultimo_login: Optional[datetime]

    class Config:
        from_attributes = True


class UsuarioPendienteDTO(BaseModel):
    """DTO para listado de usuarios pendientes"""
    id: str
    email: str
    nombre_completo: str
    creado_en: datetime

    class Config:
        from_attributes = True
```

---

## [5] SERVICIOS DE APLICACIÓN

### 5.1 Servicio de Autenticación Completo

```python
# app/aplicacion/servicios/auth_service.py

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
import secrets
import hashlib

from app.infraestructura.seguridad.hashing import hash_password, verify_password
from app.infraestructura.seguridad.jwt import crear_access_token, crear_refresh_token, verificar_token
from app.infraestructura.repos.usuario_sistema_repo import UsuarioSistemaRepo
from app.infraestructura.repos.refresh_token_repo import RefreshTokenRepo
from app.infraestructura.repos.auditoria_repo import AuditoriaRepo
from app.aplicacion.dtos.auth_dto import (
    RegistroRequestDTO, LoginRequestDTO, LoginResponseDTO,
    AprobarUsuarioDTO, UsuarioSistemaResponseDTO, UsuarioPendienteDTO,
    RefreshTokenRequestDTO
)
from app.infraestructura.db.models import EstadoUsuario, RolUsuario


class AuthService:
    """Servicio de autenticación y gestión de usuarios sistema"""

    def __init__(
        self,
        usuario_sistema_repo: UsuarioSistemaRepo,
        refresh_token_repo: RefreshTokenRepo,
        auditoria_repo: AuditoriaRepo
    ):
        self.usuario_repo = usuario_sistema_repo
        self.refresh_repo = refresh_token_repo
        self.auditoria_repo = auditoria_repo

    def registrar_usuario(self, dto: RegistroRequestDTO) -> UsuarioSistemaResponseDTO:
        """
        Registro público de usuario.
        Usuario queda en estado PENDIENTE hasta aprobación del admin.
        """
        # 1. Verificar que email no exista
        usuario_existente = self.usuario_repo.obtener_por_email(dto.email)
        if usuario_existente:
            raise ValueError("El email ya está registrado")

        # 2. Hashear password
        password_hash = hash_password(dto.password)

        # 3. Crear usuario en estado pendiente
        usuario = self.usuario_repo.crear(
            email=dto.email,
            password_hash=password_hash,
            nombre_completo=dto.nombre_completo,
            estado=EstadoUsuario.PENDIENTE,
            rol=None  # Se asigna al aprobar
        )

        # 4. Auditoría
        self.auditoria_repo.registrar(
            usuario_id=usuario.id,
            evento="USUARIO_REGISTRADO",
            detalles={"email": dto.email}
        )

        return UsuarioSistemaResponseDTO.model_validate(usuario)

    def login(self, dto: LoginRequestDTO, ip_origen: Optional[str] = None) -> LoginResponseDTO:
        """
        Login con email y password.
        Genera access token y refresh token.
        """
        # 1. Obtener usuario por email
        usuario = self.usuario_repo.obtener_por_email(dto.email)
        if not usuario:
            raise ValueError("Credenciales inválidas")

        # 2. Verificar password
        if not verify_password(dto.password, usuario.password_hash):
            self.auditoria_repo.registrar(
                usuario_id=usuario.id,
                evento="LOGIN_FALLIDO",
                detalles={"motivo": "password_incorrecto"},
                ip_origen=ip_origen
            )
            raise ValueError("Credenciales inválidas")

        # 3. Verificar que esté activo
        if usuario.estado != EstadoUsuario.ACTIVO:
            raise ValueError(
                "Tu cuenta está pendiente de aprobación. Un administrador la activará pronto."
            )

        # 4. Generar tokens
        token_family = secrets.token_urlsafe(16)

        access_token = crear_access_token({
            "user_id": str(usuario.id),
            "email": usuario.email,
            "rol": usuario.rol.value
        })

        refresh_token_raw = crear_refresh_token({
            "user_id": str(usuario.id),
            "token_family": token_family
        })

        # 5. Guardar refresh token en BD (hasheado)
        refresh_token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()
        self.refresh_repo.crear(
            usuario_id=usuario.id,
            token_hash=refresh_token_hash,
            token_family=token_family,
            expira_en=datetime.utcnow() + timedelta(days=7)
        )

        # 6. Actualizar último login
        self.usuario_repo.actualizar_ultimo_login(usuario.id)

        # 7. Auditoría
        self.auditoria_repo.registrar(
            usuario_id=usuario.id,
            evento="LOGIN_EXITOSO",
            detalles={"token_family": token_family},
            ip_origen=ip_origen
        )

        return LoginResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token_raw,
            expires_in=900,  # 15 minutos
            user=UsuarioSistemaResponseDTO.model_validate(usuario)
        )

    def refresh_access_token(self, dto: RefreshTokenRequestDTO) -> dict:
        """
        Renovar access token usando refresh token.
        Opcionalmente rota el refresh token.
        """
        # 1. Verificar refresh token
        payload = verificar_token(dto.refresh_token)
        if not payload:
            raise ValueError("Refresh token inválido o expirado")

        user_id = UUID(payload["user_id"])
        token_family = payload["token_family"]

        # 2. Verificar que el refresh token exista en BD y no esté revocado
        refresh_token_hash = hashlib.sha256(dto.refresh_token.encode()).hexdigest()
        refresh_db = self.refresh_repo.obtener_por_hash(refresh_token_hash)

        if not refresh_db or refresh_db.revocado:
            # Posible token reuse attack - revocar toda la familia
            self.refresh_repo.revocar_familia(token_family)
            raise ValueError("Refresh token revocado")

        if refresh_db.expira_en < datetime.utcnow():
            raise ValueError("Refresh token expirado")

        # 3. Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(user_id)
        if not usuario or usuario.estado != EstadoUsuario.ACTIVO:
            raise ValueError("Usuario no válido")

        # 4. Generar nuevo access token
        nuevo_access_token = crear_access_token({
            "user_id": str(usuario.id),
            "email": usuario.email,
            "rol": usuario.rol.value
        })

        # 5. Opcional: Rotar refresh token
        # (Aquí se puede implementar rotación)

        return {
            "access_token": nuevo_access_token,
            "token_type": "bearer",
            "expires_in": 900
        }

    def listar_usuarios_pendientes(self) -> List[UsuarioPendienteDTO]:
        """Listar usuarios en estado PENDIENTE (solo admin)"""
        usuarios = self.usuario_repo.obtener_por_estado(EstadoUsuario.PENDIENTE)
        return [UsuarioPendienteDTO.model_validate(u) for u in usuarios]

    def aprobar_usuario(
        self,
        usuario_id: UUID,
        dto: AprobarUsuarioDTO,
        aprobado_por_id: UUID
    ) -> UsuarioSistemaResponseDTO:
        """
        Aprobar usuario pendiente y asignar rol.
        Solo admin puede ejecutar esta acción.
        """
        # 1. Obtener usuario
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if usuario.estado != EstadoUsuario.PENDIENTE:
            raise ValueError("Usuario ya fue procesado")

        # 2. Convertir rol string a enum
        try:
            rol_enum = RolUsuario[dto.rol.upper()]
        except KeyError:
            raise ValueError(f"Rol inválido: {dto.rol}")

        # 3. Actualizar usuario
        usuario_actualizado = self.usuario_repo.aprobar(
            usuario_id=usuario_id,
            rol=rol_enum,
            profesional_id=UUID(dto.profesional_id) if dto.profesional_id else None,
            aprobado_por_id=aprobado_por_id
        )

        # 4. Auditoría
        self.auditoria_repo.registrar(
            usuario_id=aprobado_por_id,
            evento="USUARIO_APROBADO",
            detalles={
                "usuario_aprobado_id": str(usuario_id),
                "rol_asignado": dto.rol
            }
        )

        # 5. TODO: Enviar email de notificación al usuario

        return UsuarioSistemaResponseDTO.model_validate(usuario_actualizado)

    def rechazar_usuario(self, usuario_id: UUID, rechazado_por_id: UUID) -> None:
        """Rechazar usuario pendiente y eliminarlo"""
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        if not usuario or usuario.estado != EstadoUsuario.PENDIENTE:
            raise ValueError("Usuario no válido para rechazo")

        self.usuario_repo.eliminar(usuario_id)

        self.auditoria_repo.registrar(
            usuario_id=rechazado_por_id,
            evento="USUARIO_RECHAZADO",
            detalles={"usuario_rechazado_id": str(usuario_id)}
        )
```

---

