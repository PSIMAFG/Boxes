"""
Implementación del repositorio de Boxes.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.dominio.entidades import Box
from app.infraestructura.db.models import BoxModel


class BoxRepo:
    """Implementación concreta del repositorio de boxes"""

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: BoxModel) -> Box:
        """Convierte modelo SQLAlchemy a entidad del dominio"""
        return Box(
            id=model.id,
            nombre=model.nombre,
            ubicacion=model.ubicacion,
            piso=model.piso,
            capacidad=model.capacidad,
            equipamiento=model.equipamiento,
            caracteristicas=model.caracteristicas,
            activo=model.activo,
            creado_en=model.creado_en,
            actualizado_en=model.actualizado_en
        )

    def _to_model(self, entity: Box) -> BoxModel:
        """Convierte entidad del dominio a modelo SQLAlchemy"""
        return BoxModel(
            id=entity.id,
            nombre=entity.nombre,
            ubicacion=entity.ubicacion,
            piso=entity.piso,
            capacidad=entity.capacidad,
            equipamiento=entity.equipamiento,
            caracteristicas=entity.caracteristicas,
            activo=entity.activo,
            creado_en=entity.creado_en,
            actualizado_en=entity.actualizado_en
        )

    def obtener(self, id: UUID) -> Optional[Box]:
        """Obtiene box por ID"""
        model = self.db.query(BoxModel).filter(BoxModel.id == id).first()
        return self._to_entity(model) if model else None

    def crear(self, box: Box) -> Box:
        """Crea nuevo box"""
        model = self._to_model(box)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def actualizar(self, box: Box) -> Box:
        """Actualiza box existente"""
        model = self.db.query(BoxModel).filter(BoxModel.id == box.id).first()
        if not model:
            raise ValueError(f"Box {box.id} no encontrado")

        model.nombre = box.nombre
        model.ubicacion = box.ubicacion
        model.piso = box.piso
        model.capacidad = box.capacidad
        model.equipamiento = box.equipamiento
        model.caracteristicas = box.caracteristicas
        model.activo = box.activo

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def listar(self, activo: Optional[bool] = None) -> List[Box]:
        """Lista boxes con filtro opcional de activo"""
        query = self.db.query(BoxModel)

        if activo is not None:
            query = query.filter(BoxModel.activo == activo)

        models = query.all()
        return [self._to_entity(m) for m in models]

    def eliminar(self, id: UUID) -> None:
        """Elimina box (soft delete)"""
        model = self.db.query(BoxModel).filter(BoxModel.id == id).first()
        if model:
            model.activo = False
            self.db.commit()

    def obtener_por_id(self, id: UUID) -> Optional[Box]:
        """Alias para mantener compatibilidad"""
        return self.obtener(id)

    def listar_activos(self) -> List[Box]:
        """Lista solo boxes activos"""
        return self.listar(activo=True)

    def listar_todos(self) -> List[Box]:
        """Lista todos los boxes"""
        return self.listar(activo=None)
