"""
Implementación del repositorio de Profesionales.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import Profesional
from app.infraestructura.db.models import ProfesionalModel


class ProfesionalRepo:
    """Implementación concreta del repositorio de profesionales"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: ProfesionalModel) -> Profesional:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return Profesional(
            id=model.id,
            nombre=model.nombre,
            profesion=model.profesion,
            activo=model.activo,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: Profesional) -> ProfesionalModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return ProfesionalModel(
            id=entity.id,
            nombre=entity.nombre,
            profesion=entity.profesion,
            activo=entity.activo,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def obtener(self, id: UUID) -> Optional[Profesional]:
        """Obtiene profesional por ID"""
        model = self.db.query(ProfesionalModel).filter(ProfesionalModel.id == id).first()
        return self._to_entity(model) if model else None

    def crear(self, profesional: Profesional) -> Profesional:
        """Crea nuevo profesional"""
        model = self._to_model(profesional)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, profesional: Profesional) -> Profesional:
        """Actualiza profesional existente"""
        model = self.db.query(ProfesionalModel).filter(
            ProfesionalModel.id == profesional.id
        ).first()
        if not model:
            raise ValueError(f"Profesional {profesional.id} no encontrado")

        model.nombre = profesional.nombre
        model.profesion = profesional.profesion
        model.activo = profesional.activo

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar(self, activo: Optional[bool] = None) -> List[Profesional]:
        """Lista profesionales con filtro opcional de activo"""
        query = self.db.query(ProfesionalModel)

        if activo is not None:
            query = query.filter(ProfesionalModel.activo == activo)

        models = query.all()
        return [self._to_entity(m) for m in models]

    def eliminar(self, id: UUID) -> None:
        """Elimina profesional (soft delete)"""
        model = self.db.query(ProfesionalModel).filter(ProfesionalModel.id == id).first()
        if model:
            model.activo = False
            self.db.commit()
