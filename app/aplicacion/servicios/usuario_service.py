"""
Servicio de gestión de usuarios (pacientes/beneficiarios).
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from app.dominio.entidades import Usuario, AuditoriaEvento
from app.dominio.valores import RUT
from app.dominio.repositorios import IUsuarioRepo, IAuditoriaRepo
from app.aplicacion.dtos.usuario_dto import (
    UsuarioCreateDTO, UsuarioUpdateDTO, UsuarioResponseDTO
)


class UsuarioService:
    """Servicio de gestión de usuarios"""

    def __init__(self, usuario_repo: IUsuarioRepo, auditoria_repo: IAuditoriaRepo):
        self.usuario_repo = usuario_repo
        self.auditoria_repo = auditoria_repo

    def crear_usuario(self, dto: UsuarioCreateDTO, creado_por: UUID) -> UsuarioResponseDTO:
        """
        Crea un nuevo usuario.

        Args:
            dto: Datos del usuario
            creado_por: ID del usuario que crea

        Returns:
            Usuario creado

        Raises:
            ValueError: Si RUT ya existe o es inválido
        """
        # Verificar que RUT no exista
        rut = RUT(dto.rut)
        existe = self.usuario_repo.obtener_por_rut(rut)
        if existe:
            raise ValueError(f"RUT {dto.rut} ya está registrado")

        # Crear entidad
        usuario = Usuario(
            id=uuid4(),
            rut=rut,
            nombre=dto.nombre,
            fecha_nacimiento=dto.fecha_nacimiento,
            nivel_apoyo=dto.nivel_apoyo,
            activo=True,
            creado_en=datetime.utcnow(),
            actualizado_en=datetime.utcnow()
        )

        # Persistir
        usuario = self.usuario_repo.crear(usuario)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=creado_por,
            evento="usuario_creado",
            detalles={"usuario_id": str(usuario.id), "rut": usuario.rut.valor}
        ))

        return self._to_response_dto(usuario)

    def obtener_usuario(self, usuario_id: UUID) -> Optional[UsuarioResponseDTO]:
        """Obtiene usuario por ID"""
        usuario = self.usuario_repo.obtener(usuario_id)
        return self._to_response_dto(usuario) if usuario else None

    def obtener_por_rut(self, rut: str) -> Optional[UsuarioResponseDTO]:
        """Obtiene usuario por RUT"""
        usuario = self.usuario_repo.obtener_por_rut(RUT(rut))
        return self._to_response_dto(usuario) if usuario else None

    def actualizar_usuario(
        self,
        usuario_id: UUID,
        dto: UsuarioUpdateDTO,
        actualizado_por: UUID
    ) -> UsuarioResponseDTO:
        """Actualiza un usuario existente"""
        usuario = self.usuario_repo.obtener(usuario_id)
        if not usuario:
            raise ValueError(f"Usuario {usuario_id} no encontrado")

        # Actualizar campos
        if dto.nombre:
            usuario.nombre = dto.nombre
        if dto.fecha_nacimiento:
            usuario.fecha_nacimiento = dto.fecha_nacimiento
        if dto.nivel_apoyo is not None:
            usuario.nivel_apoyo = dto.nivel_apoyo
        if dto.activo is not None:
            usuario.activo = dto.activo

        usuario.actualizado_en = datetime.utcnow()

        # Persistir
        usuario = self.usuario_repo.actualizar(usuario)

        # Auditar
        self.auditoria_repo.registrar_evento(AuditoriaEvento(
            usuario_id=actualizado_por,
            evento="usuario_actualizado",
            detalles={"usuario_id": str(usuario_id)}
        ))

        return self._to_response_dto(usuario)

    def listar_usuarios(
        self,
        activo: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UsuarioResponseDTO]:
        """Lista usuarios con filtros"""
        usuarios = self.usuario_repo.listar(activo=activo, limit=limit, offset=offset)
        return [self._to_response_dto(u) for u in usuarios]

    def _to_response_dto(self, usuario: Usuario) -> UsuarioResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UsuarioResponseDTO(
            id=usuario.id,
            rut=usuario.rut.valor,
            nombre=usuario.nombre,
            fecha_nacimiento=usuario.fecha_nacimiento,
            nivel_apoyo=usuario.nivel_apoyo,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
            actualizado_en=usuario.actualizado_en,
            edad=usuario.edad()
        )
