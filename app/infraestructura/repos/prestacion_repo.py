"""
Implementación del repositorio de Prestaciones.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import Prestacion
from app.infraestructura.db.models import PrestacionModel


class PrestacionRepo:
    """Implementación concreta del repositorio de prestaciones"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: PrestacionModel) -> Prestacion:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return Prestacion(
            id=model.id,
            nombre=model.nombre,
            duracion_minutos=model.duracion_minutos,
            periodicidad_dias=model.periodicidad_dias,
            tolerancia_dias=model.tolerancia_dias,
            habilitada=model.habilitada,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: Prestacion) -> PrestacionModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return PrestacionModel(
            id=entity.id,
            nombre=entity.nombre,
            duracion_minutos=entity.duracion_minutos,
            periodicidad_dias=entity.periodicidad_dias,
            tolerancia_dias=entity.tolerancia_dias,
            habilitada=entity.habilitada,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def obtener(self, id: UUID) -> Optional[Prestacion]:
        """Obtiene prestacion por ID"""
        model = self.db.query(PrestacionModel).filter(PrestacionModel.id == id).first()
        return self._to_entity(model) if model else None

    def crear(self, prestacion: Prestacion) -> Prestacion:
        """Crea nueva prestacion"""
        model = self._to_model(prestacion)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, prestacion: Prestacion) -> Prestacion:
        """Actualiza prestacion existente"""
        model = self.db.query(PrestacionModel).filter(
            PrestacionModel.id == prestacion.id
        ).first()
        if not model:
            raise ValueError(f"Prestacion {prestacion.id} no encontrada")

        model.nombre = prestacion.nombre
        model.duracion_minutos = prestacion.duracion_minutos
        model.periodicidad_dias = prestacion.periodicidad_dias
        model.tolerancia_dias = prestacion.tolerancia_dias
        model.habilitada = prestacion.habilitada

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar(self, habilitada: Optional[bool] = None) -> List[Prestacion]:
        """Lista prestaciones con filtro opcional de habilitada"""
        query = self.db.query(PrestacionModel)

        if habilitada is not None:
            query = query.filter(PrestacionModel.habilitada == habilitada)

        models = query.all()
        return [self._to_entity(m) for m in models]

    def eliminar(self, id: UUID) -> None:
        """Elimina prestacion (soft delete)"""
        model = self.db.query(PrestacionModel).filter(PrestacionModel.id == id).first()
        if model:
            model.habilitada = False
            self.db.commit()
