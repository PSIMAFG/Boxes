"""
Implementación del repositorio de Agenda (Citas y Bloqueos).
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.dominio.entidades import Cita, Bloqueo
from app.infraestructura.db.models import CitaModel, BloqueoModel, EstadoCita, ScopeBloqueo


class AgendaRepo:
    """Implementación concreta del repositorio de agenda"""

    def __init__(self, db: Session):
        self.db = db

    def _cita_to_entity(self, model: CitaModel) -> Cita:
        """Convierte modelo SQLAlchemy de cita a entidad del dominio"""
        return Cita(
            id=model.id,
            usuario_id=model.usuario_id,
            profesional_id=model.profesional_id,
            prestacion_id=model.prestacion_id,
            box_id=model.box_id,
            inicio=model.inicio,
            fin=model.fin,
            estado=model.estado.value,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _cita_to_model(self, entity: Cita) -> CitaModel:
        """Convierte entidad de cita a modelo SQLAlchemy"""
        return CitaModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            profesional_id=entity.profesional_id,
            prestacion_id=entity.prestacion_id,
            box_id=entity.box_id,
            inicio=entity.inicio,
            fin=entity.fin,
            estado=EstadoCita(entity.estado),
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def _bloqueo_to_entity(self, model: BloqueoModel) -> Bloqueo:
        """Convierte modelo SQLAlchemy de bloqueo a entidad del dominio"""
        return Bloqueo(
            id=model.id,
            scope=model.scope.value,
            box_id=model.box_id,
            profesional_id=model.profesional_id,
            inicio=model.inicio,
            fin=model.fin,
            motivo=model.motivo,
            creado_en=model.creado_en,
            creado_por=model.creado_por
        )

    def _bloqueo_to_model(self, entity: Bloqueo) -> BloqueoModel:
        """Convierte entidad de bloqueo a modelo SQLAlchemy"""
        return BloqueoModel(
            id=entity.id,
            scope=ScopeBloqueo(entity.scope),
            box_id=entity.box_id,
            profesional_id=entity.profesional_id,
            inicio=entity.inicio,
            fin=entity.fin,
            motivo=entity.motivo,
            creado_en=entity.creado_en,
            creado_por=entity.creado_por
        )

    def buscar_citas(
        self,
        profesional_id: Optional[UUID] = None,
        box_id: Optional[UUID] = None,
        usuario_id: Optional[UUID] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None
    ) -> List[Cita]:
        """Busca citas con filtros opcionales"""
        query = self.db.query(CitaModel)

        if profesional_id:
            query = query.filter(CitaModel.profesional_id == profesional_id)
        if box_id:
            query = query.filter(CitaModel.box_id == box_id)
        if usuario_id:
            query = query.filter(CitaModel.usuario_id == usuario_id)
        if fecha_desde:
            query = query.filter(CitaModel.inicio >= fecha_desde)
        if fecha_hasta:
            query = query.filter(CitaModel.fin <= fecha_hasta)
        if estado:
            query = query.filter(CitaModel.estado == EstadoCita(estado))

        models = query.order_by(CitaModel.inicio).all()
        return [self._cita_to_entity(m) for m in models]

    def crear_cita(self, cita: Cita) -> Cita:
        """Crea nueva cita"""
        model = self._cita_to_model(cita)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._cita_to_entity(model)

    def obtener_cita(self, cita_id: UUID) -> Optional[Cita]:
        """Obtiene cita por ID"""
        model = self.db.query(CitaModel).filter(CitaModel.id == cita_id).first()
        return self._cita_to_entity(model) if model else None

    def actualizar_cita(self, cita: Cita) -> Cita:
        """Actualiza cita existente"""
        model = self.db.query(CitaModel).filter(CitaModel.id == cita.id).first()
        if not model:
            raise ValueError(f"Cita {cita.id} no encontrada")

        model.usuario_id = cita.usuario_id
        model.profesional_id = cita.profesional_id
        model.prestacion_id = cita.prestacion_id
        model.box_id = cita.box_id
        model.inicio = cita.inicio
        model.fin = cita.fin
        model.estado = EstadoCita(cita.estado)

        self.db.commit()
        self.db.refresh(model)
        return self._cita_to_entity(model)

    def actualizar_estado(self, cita_id: UUID, estado: str) -> None:
        """Actualiza estado de una cita"""
        model = self.db.query(CitaModel).filter(CitaModel.id == cita_id).first()
        if model:
            model.estado = EstadoCita(estado)
            self.db.commit()

    def hay_solape(
        self,
        profesional_id: UUID,
        box_id: UUID,
        inicio: datetime,
        fin: datetime,
        excluir_cita_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica si existe solape temporal para profesional y box.
        Solo considera citas en estados programada o confirmada.
        """
        query = self.db.query(CitaModel).filter(
            and_(
                or_(
                    CitaModel.profesional_id == profesional_id,
                    CitaModel.box_id == box_id
                ),
                CitaModel.estado.in_([EstadoCita.PROGRAMADA, EstadoCita.CONFIRMADA]),
                # Condición de solapamiento: NOT (fin <= inicio OR inicio >= fin)
                or_(
                    and_(CitaModel.inicio < fin, CitaModel.fin > inicio)
                )
            )
        )

        if excluir_cita_id:
            query = query.filter(CitaModel.id != excluir_cita_id)

        return query.count() > 0

    def obtener_ultima_cita_usuario_prestacion(
        self,
        usuario_id: UUID,
        prestacion_id: UUID
    ) -> Optional[Cita]:
        """Obtiene última cita cumplida de usuario para prestación específica"""
        model = (
            self.db.query(CitaModel)
            .filter(
                CitaModel.usuario_id == usuario_id,
                CitaModel.prestacion_id == prestacion_id,
                CitaModel.estado == EstadoCita.CUMPLIDA
            )
            .order_by(CitaModel.fin.desc())
            .first()
        )
        return self._cita_to_entity(model) if model else None

    def crear_bloqueo(self, bloqueo: Bloqueo) -> Bloqueo:
        """Crea nuevo bloqueo"""
        model = self._bloqueo_to_model(bloqueo)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._bloqueo_to_entity(model)

    def listar_bloqueos(
        self,
        profesional_id: Optional[UUID] = None,
        box_id: Optional[UUID] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> List[Bloqueo]:
        """Lista bloqueos con filtros opcionales"""
        query = self.db.query(BloqueoModel)

        if profesional_id:
            query = query.filter(BloqueoModel.profesional_id == profesional_id)
        if box_id:
            query = query.filter(BloqueoModel.box_id == box_id)
        if fecha_desde:
            query = query.filter(BloqueoModel.inicio >= fecha_desde)
        if fecha_hasta:
            query = query.filter(BloqueoModel.fin <= fecha_hasta)

        models = query.order_by(BloqueoModel.inicio).all()
        return [self._bloqueo_to_entity(m) for m in models]
