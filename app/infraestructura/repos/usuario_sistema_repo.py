"""
Implementación del repositorio de UsuariosSistema.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import UsuarioSistema
from app.infraestructura.db.models import UsuarioSistemaModel, RolUsuario


class UsuarioSistemaRepo:
    """Implementación concreta del repositorio de usuarios del sistema"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UsuarioSistemaModel) -> UsuarioSistema:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return UsuarioSistema(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            rol=model.rol.value,
            activo=model.activo,
            profesional_id=model.profesional_id,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: UsuarioSistema) -> UsuarioSistemaModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return UsuarioSistemaModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            rol=RolUsuario(entity.rol),
            activo=entity.activo,
            profesional_id=entity.profesional_id,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def obtener_por_email(self, email: str) -> Optional[UsuarioSistema]:
        """Busca usuario del sistema por email"""
        model = self.db.query(UsuarioSistemaModel).filter(
            UsuarioSistemaModel.email == email
        ).first()
        return self._to_entity(model) if model else None

    def obtener(self, id: UUID) -> Optional[UsuarioSistema]:
        """Obtiene usuario del sistema por ID"""
        model = self.db.query(UsuarioSistemaModel).filter(
            UsuarioSistemaModel.id == id
        ).first()
        return self._to_entity(model) if model else None

    def crear(self, usuario: UsuarioSistema) -> UsuarioSistema:
        """Crea nuevo usuario del sistema"""
        model = self._to_model(usuario)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, usuario: UsuarioSistema) -> UsuarioSistema:
        """Actualiza usuario del sistema existente"""
        model = self.db.query(UsuarioSistemaModel).filter(
            UsuarioSistemaModel.id == usuario.id
        ).first()
        if not model:
            raise ValueError(f"UsuarioSistema {usuario.id} no encontrado")

        model.email = usuario.email
        model.password_hash = usuario.password_hash
        model.rol = RolUsuario(usuario.rol)
        model.activo = usuario.activo
        model.profesional_id = usuario.profesional_id

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar(self, activo: Optional[bool] = None) -> List[UsuarioSistema]:
        """Lista usuarios del sistema"""
        query = self.db.query(UsuarioSistemaModel)

        if activo is not None:
            query = query.filter(UsuarioSistemaModel.activo == activo)

        models = query.all()
        return [self._to_entity(m) for m in models]
