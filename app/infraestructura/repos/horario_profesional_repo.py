"""
Implementación del repositorio de HorarioProfesional.
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import HorarioProfesional
from app.infraestructura.db.models import HorarioProfesionalModel


class HorarioProfesionalRepo:
    """Implementación concreta del repositorio de horarios profesionales"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: HorarioProfesionalModel) -> HorarioProfesional:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return HorarioProfesional(
            id=model.id,
            profesional_id=model.profesional_id,
            dia_semana=model.dia_semana,
            hora_inicio=model.hora_inicio,
            hora_fin=model.hora_fin,
            box_preferido_id=model.box_preferido_id,
            activo=model.activo,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: HorarioProfesional) -> HorarioProfesionalModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return HorarioProfesionalModel(
            id=entity.id,
            profesional_id=entity.profesional_id,
            dia_semana=entity.dia_semana,
            hora_inicio=entity.hora_inicio,
            hora_fin=entity.hora_fin,
            box_preferido_id=entity.box_preferido_id,
            activo=entity.activo,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def listar_por_profesional(self, profesional_id: UUID) -> List[HorarioProfesional]:
        """Lista horarios de un profesional"""
        models = self.db.query(HorarioProfesionalModel).filter(
            HorarioProfesionalModel.profesional_id == profesional_id,
            HorarioProfesionalModel.activo == True
        ).order_by(HorarioProfesionalModel.dia_semana).all()
        return [self._to_entity(m) for m in models]

    def crear(self, horario: HorarioProfesional) -> HorarioProfesional:
        """Crea nuevo horario"""
        model = self._to_model(horario)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, horario: HorarioProfesional) -> HorarioProfesional:
        """Actualiza horario existente"""
        model = self.db.query(HorarioProfesionalModel).filter(
            HorarioProfesionalModel.id == horario.id
        ).first()
        if not model:
            raise ValueError(f"Horario {horario.id} no encontrado")

        model.dia_semana = horario.dia_semana
        model.hora_inicio = horario.hora_inicio
        model.hora_fin = horario.hora_fin
        model.box_preferido_id = horario.box_preferido_id
        model.activo = horario.activo

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def eliminar(self, id: UUID) -> None:
        """Elimina horario"""
        model = self.db.query(HorarioProfesionalModel).filter(
            HorarioProfesionalModel.id == id
        ).first()
        if model:
            model.activo = False
            self.db.commit()
