"""
Implementación del repositorio de Auditoría.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.dominio.entidades import AuditoriaEvento
from app.infraestructura.db.models import AuditoriaEventoModel


class AuditoriaRepo:
    """Implementación concreta del repositorio de auditoría"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: AuditoriaEventoModel) -> AuditoriaEvento:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return AuditoriaEvento(
            id=model.id,
            usuario_id=model.usuario_id,
            evento=model.evento,
            detalles=model.detalles,
            timestamp=model.timestamp,
            ip_origen=model.ip_origen
        )

    def _to_model(self, entity: AuditoriaEvento) -> AuditoriaEventoModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return AuditoriaEventoModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            evento=entity.evento,
            detalles=entity.detalles,
            timestamp=entity.timestamp,
            ip_origen=entity.ip_origen
        )

    def registrar_evento(self, evento: AuditoriaEvento) -> AuditoriaEvento:
        """Registra evento de auditoría"""
        model = self._to_model(evento)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar_eventos(
        self,
        usuario_id: Optional[UUID] = None,
        evento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditoriaEvento]:
        """Lista eventos de auditoría con filtros"""
        query = self.db.query(AuditoriaEventoModel)

        if usuario_id:
            query = query.filter(AuditoriaEventoModel.usuario_id == usuario_id)
        if evento:
            query = query.filter(AuditoriaEventoModel.evento == evento)
        if fecha_desde:
            query = query.filter(AuditoriaEventoModel.timestamp >= fecha_desde)
        if fecha_hasta:
            query = query.filter(AuditoriaEventoModel.timestamp <= fecha_hasta)

        models = query.order_by(AuditoriaEventoModel.timestamp.desc()).limit(limit).all()
        return [self._to_entity(m) for m in models]
