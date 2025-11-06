"""
Servicio de autenticación y gestión de usuarios del sistema.
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from app.dominio.entidades import UsuarioSistema, AuditoriaEvento
from app.dominio.repositorios import IUsuarioSistemaRepo, IAuditoriaRepo
from app.infraestructura.seguridad.hashing import hash_password, verificar_password
from app.infraestructura.seguridad.jwt import crear_token
from app.aplicacion.dtos.auth_dto import (
    LoginRequestDTO, LoginResponseDTO,
    UsuarioSistemaCreateDTO, UsuarioSistemaResponseDTO
)


class AuthService:
    """Servicio de autenticación"""

    def __init__(
        self,
        usuario_sistema_repo: IUsuarioSistemaRepo,
        auditoria_repo: IAuditoriaRepo
    ):
        self.usuario_sistema_repo = usuario_sistema_repo
        self.auditoria_repo = auditoria_repo

    def login(self, dto: LoginRequestDTO, ip_origen: Optional[str] = None) -> LoginResponseDTO:
        """
        Autentica un usuario y retorna JWT token.

        Args:
            dto: Credenciales de login
            ip_origen: IP del cliente (para auditoría)

        Returns:
            Token JWT y datos del usuario

        Raises:
            ValueError: Si credenciales inválidas
        """
        # Buscar usuario
        usuario = self.usuario_sistema_repo.obtener_por_email(dto.email)
        if not usuario:
            raise ValueError("Email o contraseña incorrectos")

        # Verificar contraseña
        if not verificar_password(dto.password, usuario.password_hash):
            # Auditar intento fallido
            self.auditoria_repo.registrar_evento(AuditoriaEvento(
                usuario_id=usuario.id,
                evento="login_fallido",
                detalles={"email": dto.email},
                ip_origen=ip_origen
            ))
            raise ValueError("Email o contraseña incorrectos")

        # Verificar que usuario esté activo
        if not usuario.activo:
            raise ValueError("Usuario desactivado")

        # Crear token
        token_data = {
            "user_id": str(usuario.id),
            "email": usuario.email,
            "rol": usuario.rol
        }
        token = crear_token(token_data)

        # Auditar login exitoso
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=usuario.id,
            evento="login_exitoso",
            detalles={"email": dto.email},
            ip_origen=ip_origen
        ))

        return LoginResponseDTO(
            access_token=token,
            token_type="bearer",
            user_id=usuario.id,
            email=usuario.email,
            rol=usuario.rol
        )

    def crear_usuario_sistema(
        self,
        dto: UsuarioSistemaCreateDTO,
        creado_por: UUID
    ) -> UsuarioSistemaResponseDTO:
        """
        Crea un nuevo usuario del sistema.
        Solo admins pueden crear usuarios.

        Args:
            dto: Datos del usuario a crear
            creado_por: ID del admin que crea el usuario

        Returns:
            Usuario creado

        Raises:
            ValueError: Si email ya existe
        """
        # Verificar que email no exista
        existe = self.usuario_sistema_repo.obtener_por_email(dto.email)
        if existe:
            raise ValueError(f"Email {dto.email} ya está registrado")

        # Crear entidad
        usuario = UsuarioSistema(
            id=uuid4(),
            email=dto.email,
            password_hash=hash_password(dto.password),
            rol=dto.rol,
            activo=True,
            profesional_id=dto.profesional_id,
            creado_en=datetime.utcnow(),
            actualizado_en=datetime.utcnow()
        )

        # Persistir
        usuario = self.usuario_sistema_repo.crear(usuario)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=creado_por,
            evento="usuario_sistema_creado",
            detalles={
                "nuevo_usuario_id": str(usuario.id),
                "email": usuario.email,
                "rol": usuario.rol
            }
        ))

        return UsuarioSistemaResponseDTO(
            id=usuario.id,
            email=usuario.email,
            rol=usuario.rol,
            activo=usuario.activo,
            profesional_id=usuario.profesional_id
        )

    def obtener_usuario(self, usuario_id: UUID) -> Optional[UsuarioSistemaResponseDTO]:
        """Obtiene usuario del sistema por ID"""
        usuario = self.usuario_sistema_repo.obtener(usuario_id)
        if not usuario:
            return None

        return UsuarioSistemaResponseDTO(
            id=usuario.id,
            email=usuario.email,
            rol=usuario.rol,
            activo=usuario.activo,
            profesional_id=usuario.profesional_id
        )

    def cambiar_password(
        self,
        usuario_id: UUID,
        password_actual: str,
        password_nuevo: str
    ) -> None:
        """
        Cambia la contraseña de un usuario.

        Args:
            usuario_id: ID del usuario
            password_actual: Contraseña actual
            password_nuevo: Nueva contraseña

        Raises:
            ValueError: Si contraseña actual incorrecta o usuario no encontrado
        """
        usuario = self.usuario_sistema_repo.obtener(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Verificar contraseña actual
        if not verificar_password(password_actual, usuario.password_hash):
            raise ValueError("Contraseña actual incorrecta")

        # Actualizar
        usuario.password_hash = hash_password(password_nuevo)
        usuario.actualizado_en = datetime.utcnow()
        self.usuario_sistema_repo.actualizar(usuario)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=usuario_id,
            evento="password_cambiado"
        ))
