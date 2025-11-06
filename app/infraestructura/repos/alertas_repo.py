"""
Implementación del repositorio de Alertas.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.dominio.entidades import Alerta
from app.infraestructura.db.models import AlertaModel, NivelAlerta


class AlertasRepo:
    """Implementación concreta del repositorio de alertas"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: AlertaModel) -> Alerta:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return Alerta(
            id=model.id,
            usuario_id=model.usuario_id,
            prestacion_id=model.prestacion_id,
            nivel=model.nivel.value,
            motivo=model.motivo,
            fecha_objetivo=model.fecha_objetivo,
            resuelta=model.resuelta,
            creado_en=model.creado_en,
            resuelta_en=model.resuelta_en
        )

    def _to_model(self, entity: Alerta) -> AlertaModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return AlertaModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            prestacion_id=entity.prestacion_id,
            nivel=NivelAlerta(entity.nivel),
            motivo=entity.motivo,
            fecha_objetivo=entity.fecha_objetivo,
            resuelta=entity.resuelta,
            creado_en=entity.creado_en,
            resuelta_en=entity.resuelta_en
        )

    def crear(self, alerta: Alerta) -> Alerta:
        """Crea nueva alerta"""
        model = self._to_model(alerta)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar_pendientes(
        self,
        usuario_id: Optional[UUID] = None,
        nivel: Optional[str] = None
    ) -> List[Alerta]:
        """Lista alertas no resueltas con filtros opcionales"""
        query = self.db.query(AlertaModel).filter(AlertaModel.resuelta == False)

        if usuario_id:
            query = query.filter(AlertaModel.usuario_id == usuario_id)
        if nivel:
            query = query.filter(AlertaModel.nivel == NivelAlerta(nivel))

        models = query.order_by(
            AlertaModel.nivel.desc(),
            AlertaModel.fecha_objetivo
        ).all()
        return [self._to_entity(m) for m in models]

    def marcar_resuelta(self, alerta_id: UUID) -> None:
        """Marca alerta como resuelta"""
        model = self.db.query(AlertaModel).filter(AlertaModel.id == alerta_id).first()
        if model:
            model.resuelta = True
            model.resuelta_en = datetime.utcnow()
            self.db.commit()

    def obtener(self, alerta_id: UUID) -> Optional[Alerta]:
        """Obtiene alerta por ID"""
        model = self.db.query(AlertaModel).filter(AlertaModel.id == alerta_id).first()
        return self._to_entity(model) if model else None
