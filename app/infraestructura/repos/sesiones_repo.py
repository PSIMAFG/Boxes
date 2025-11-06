"""
Implementación del repositorio de Sesiones.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import SesionRegistro
from app.infraestructura.db.models import SesionRegistroModel, ValoracionSesion


class SesionesRepo:
    """Implementación concreta del repositorio de sesiones"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: SesionRegistroModel) -> SesionRegistro:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return SesionRegistro(
            id=model.id,
            cita_id=model.cita_id,
            cumplida=model.cumplida,
            valoracion=model.valoracion.value if model.valoracion else None,
            notas=model.notas,
            creado_por=model.creado_por,
            creado_en=model.creado_en
        )

    def _to_model(self, entity: SesionRegistro) -> SesionRegistroModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return SesionRegistroModel(
            id=entity.id,
            cita_id=entity.cita_id,
            cumplida=entity.cumplida,
            valoracion=ValoracionSesion(entity.valoracion) if entity.valoracion else None,
            notas=entity.notas,
            creado_por=entity.creado_por,
            creado_en=entity.creado_en
        )

    def crear_registro(self, sesion: SesionRegistro) -> SesionRegistro:
        """Crea nuevo registro de sesión"""
        model = self._to_model(sesion)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def obtener_por_cita(self, cita_id: UUID) -> Optional[SesionRegistro]:
        """Obtiene registro de sesión por ID de cita"""
        model = self.db.query(SesionRegistroModel).filter(
            SesionRegistroModel.cita_id == cita_id
        ).first()
        return self._to_entity(model) if model else None

    def listar_por_usuario(self, usuario_id: UUID, limit: int = 100) -> List[SesionRegistro]:
        """Lista registros de sesión por usuario"""
        # Necesitamos hacer join con citas para filtrar por usuario_id
        from app.infraestructura.db.models import CitaModel

        models = (
            self.db.query(SesionRegistroModel)
            .join(CitaModel, CitaModel.id == SesionRegistroModel.cita_id)
            .filter(CitaModel.usuario_id == usuario_id)
            .order_by(SesionRegistroModel.creado_en.desc())
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]
