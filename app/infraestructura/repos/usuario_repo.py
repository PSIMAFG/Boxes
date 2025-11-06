"""
Implementación del repositorio de Usuarios.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import Usuario
from app.dominio.valores import RUT
from app.infraestructura.db.models import UsuarioModel


class UsuarioRepo:
    """Implementación concreta del repositorio de usuarios"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UsuarioModel) -> Usuario:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return Usuario(
            id=model.id,
            rut=RUT(model.rut),
            nombre=model.nombre,
            fecha_nacimiento=model.fecha_nacimiento,
            nivel_apoyo=model.nivel_apoyo,
            activo=model.activo,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: Usuario) -> UsuarioModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return UsuarioModel(
            id=entity.id,
            rut=entity.rut.valor,
            nombre=entity.nombre,
            fecha_nacimiento=entity.fecha_nacimiento,
            nivel_apoyo=entity.nivel_apoyo,
            activo=entity.activo,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def obtener_por_rut(self, rut: RUT) -> Optional[Usuario]:
        """Busca usuario por RUT"""
        model = self.db.query(UsuarioModel).filter(UsuarioModel.rut == rut.valor).first()
        return self._to_entity(model) if model else None

    def obtener(self, id: UUID) -> Optional[Usuario]:
        """Obtiene usuario por ID"""
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        return self._to_entity(model) if model else None

    def crear(self, usuario: Usuario) -> Usuario:
        """Crea nuevo usuario"""
        model = self._to_model(usuario)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, usuario: Usuario) -> Usuario:
        """Actualiza usuario existente"""
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
        if not model:
            raise ValueError(f"Usuario {usuario.id} no encontrado")

        model.rut = usuario.rut.valor
        model.nombre = usuario.nombre
        model.fecha_nacimiento = usuario.fecha_nacimiento
        model.nivel_apoyo = usuario.nivel_apoyo
        model.activo = usuario.activo

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar(
        self,
        activo: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Usuario]:
        """Lista usuarios con filtro opcional de activo"""
        query = self.db.query(UsuarioModel)

        if activo is not None:
            query = query.filter(UsuarioModel.activo == activo)

        models = query.limit(limit).offset(offset).all()
        return [self._to_entity(m) for m in models]

    def eliminar(self, id: UUID) -> None:
        """Elimina usuario (soft delete)"""
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        if model:
            model.activo = False
            self.db.commit()
