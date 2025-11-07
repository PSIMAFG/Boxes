"""
Servicio de análisis y estadísticas de uso de boxes.

Calcula métricas de ocupación hora a hora, día a día, semana a semana.
"""
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from collections import defaultdict
import calendar

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.dominio.entidades import Box, Cita, HistorialBox
from app.aplicacion.dtos.analitica_dto import (
    UsoHorarioDTO,
    UsoDiarioDTO,
    UsoSemanalDTO,
    EstadisticaBoxDTO,
    ComparativaBoxesDTO,
    HistorialBoxDTO,
    FiltroEstadisticasDTO
)


class AnaliticaBoxService:
    """Servicio para análisis de uso de boxes"""

    def __init__(self, db: Session):
        self.db = db

    def obtener_uso_horario(
        self,
        box_id: UUID,
        fecha: date
    ) -> List[UsoHorarioDTO]:
        """
        Calcula el uso de un box hora por hora en un día específico.

        Args:
            box_id: ID del box a analizar
            fecha: Fecha del día a analizar

        Returns:
            Lista con uso de cada hora del día (0-23)
        """
        # Obtener citas del box en esa fecha
        inicio_dia = datetime.combine(fecha, time.min)
        fin_dia = datetime.combine(fecha, time.max)

        citas = self.db.query(Cita).filter(
            and_(
                Cita.box_id == box_id,
                Cita.inicio >= inicio_dia,
                Cita.inicio <= fin_dia,
                Cita.estado.in_(["programada", "confirmada", "cumplida"])
            )
        ).all()

        # Calcular minutos ocupados por hora
        uso_por_hora = {}
        for hora in range(24):
            uso_por_hora[hora] = {
                "minutos_ocupados": 0,
                "numero_citas": 0
            }

        for cita in citas:
            # Calcular qué horas ocupa esta cita
            inicio_hora = cita.inicio.hour
            fin_hora = cita.fin.hour

            # Si la cita empieza y termina en la misma hora
            if inicio_hora == fin_hora:
                minutos = (cita.fin - cita.inicio).total_seconds() / 60
                uso_por_hora[inicio_hora]["minutos_ocupados"] += minutos
                uso_por_hora[inicio_hora]["numero_citas"] += 1
            else:
                # Primera hora parcial
                minutos_primera_hora = 60 - cita.inicio.minute
                uso_por_hora[inicio_hora]["minutos_ocupados"] += minutos_primera_hora
                uso_por_hora[inicio_hora]["numero_citas"] += 1

                # Horas completas intermedias
                for hora in range(inicio_hora + 1, fin_hora):
                    uso_por_hora[hora]["minutos_ocupados"] += 60
                    uso_por_hora[hora]["numero_citas"] += 1

                # Última hora parcial
                if cita.fin.minute > 0:
                    uso_por_hora[fin_hora]["minutos_ocupados"] += cita.fin.minute
                    uso_por_hora[fin_hora]["numero_citas"] += 1

        # Convertir a DTOs
        resultado = []
        for hora in range(24):
            minutos_ocupados = int(uso_por_hora[hora]["minutos_ocupados"])
            minutos_disponibles = 60
            porcentaje = (minutos_ocupados / minutos_disponibles * 100) if minutos_disponibles > 0 else 0

            resultado.append(UsoHorarioDTO(
                hora=hora,
                minutos_ocupados=minutos_ocupados,
                minutos_disponibles=minutos_disponibles,
                porcentaje_uso=round(porcentaje, 2),
                numero_citas=uso_por_hora[hora]["numero_citas"]
            ))

        return resultado

    def obtener_uso_diario(
        self,
        box_id: UUID,
        fecha: date,
        incluir_horas: bool = False
    ) -> UsoDiarioDTO:
        """
        Calcula el uso de un box en un día completo.

        Args:
            box_id: ID del box a analizar
            fecha: Fecha del día a analizar
            incluir_horas: Si incluir detalle hora por hora

        Returns:
            Estadísticas de uso del día
        """
        uso_horas = self.obtener_uso_horario(box_id, fecha)

        # Agregar totales
        total_minutos_ocupados = sum(h.minutos_ocupados for h in uso_horas)
        total_minutos_disponibles = sum(h.minutos_disponibles for h in uso_horas)
        total_citas = sum(h.numero_citas for h in uso_horas)

        porcentaje_uso = (
            (total_minutos_ocupados / total_minutos_disponibles * 100)
            if total_minutos_disponibles > 0 else 0
        )

        # Nombre del día de la semana en español
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_semana = dias_semana[fecha.weekday()]

        return UsoDiarioDTO(
            fecha=fecha,
            dia_semana=dia_semana,
            minutos_ocupados=total_minutos_ocupados,
            minutos_disponibles=total_minutos_disponibles,
            porcentaje_uso=round(porcentaje_uso, 2),
            numero_citas=total_citas,
            uso_por_hora=uso_horas if incluir_horas else []
        )

    def obtener_uso_semanal(
        self,
        box_id: UUID,
        fecha: date,
        incluir_dias: bool = False
    ) -> UsoSemanalDTO:
        """
        Calcula el uso de un box en una semana completa.

        Args:
            box_id: ID del box a analizar
            fecha: Cualquier fecha dentro de la semana a analizar
            incluir_dias: Si incluir detalle día por día

        Returns:
            Estadísticas de uso de la semana
        """
        # Calcular inicio y fin de la semana (lunes a domingo)
        inicio_semana = fecha - timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + timedelta(days=6)

        # Calcular número de semana
        semana = fecha.isocalendar()[1]
        año = fecha.year

        # Obtener uso de cada día
        uso_dias = []
        total_minutos_ocupados = 0
        total_minutos_disponibles = 0
        total_citas = 0

        for i in range(7):
            dia = inicio_semana + timedelta(days=i)
            uso_dia = self.obtener_uso_diario(box_id, dia, incluir_horas=False)

            if incluir_dias:
                uso_dias.append(uso_dia)

            total_minutos_ocupados += uso_dia.minutos_ocupados
            total_minutos_disponibles += uso_dia.minutos_disponibles
            total_citas += uso_dia.numero_citas

        porcentaje_uso = (
            (total_minutos_ocupados / total_minutos_disponibles * 100)
            if total_minutos_disponibles > 0 else 0
        )

        return UsoSemanalDTO(
            semana=semana,
            año=año,
            fecha_inicio=inicio_semana,
            fecha_fin=fin_semana,
            minutos_ocupados=total_minutos_ocupados,
            minutos_disponibles=total_minutos_disponibles,
            porcentaje_uso=round(porcentaje_uso, 2),
            numero_citas=total_citas,
            uso_por_dia=uso_dias
        )

    def obtener_estadisticas_box(
        self,
        box_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> EstadisticaBoxDTO:
        """
        Obtiene estadísticas completas de un box en un período.

        Args:
            box_id: ID del box
            fecha_inicio: Inicio del período
            fecha_fin: Fin del período

        Returns:
            Estadísticas del box en el período
        """
        # Obtener box
        box = self.db.query(Box).filter(Box.id == box_id).first()
        if not box:
            raise ValueError(f"Box con ID {box_id} no encontrado")

        # Obtener citas en el período
        citas = self.db.query(Cita).filter(
            and_(
                Cita.box_id == box_id,
                Cita.inicio >= fecha_inicio,
                Cita.inicio <= fecha_fin,
                Cita.estado.in_(["programada", "confirmada", "cumplida"])
            )
        ).all()

        # Calcular minutos ocupados
        total_minutos_ocupados = sum(
            int((cita.fin - cita.inicio).total_seconds() / 60)
            for cita in citas
        )

        # Calcular minutos disponibles (8 horas por día)
        dias = (fecha_fin.date() - fecha_inicio.date()).days + 1
        total_minutos_disponibles = dias * 8 * 60  # 8 horas por día

        porcentaje_uso = (
            (total_minutos_ocupados / total_minutos_disponibles * 100)
            if total_minutos_disponibles > 0 else 0
        )

        return EstadisticaBoxDTO(
            box_id=box.id,
            box_nombre=box.nombre,
            piso=box.piso,
            capacidad=box.capacidad,
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            total_minutos_ocupados=total_minutos_ocupados,
            total_minutos_disponibles=total_minutos_disponibles,
            porcentaje_uso_promedio=round(porcentaje_uso, 2),
            total_citas=len(citas),
            uso_piso=None  # Se calcula en comparativa
        )

    def obtener_comparativa_boxes(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        box_ids: Optional[List[UUID]] = None,
        piso: Optional[int] = None,
        incluir_inactivos: bool = False
    ) -> ComparativaBoxesDTO:
        """
        Compara el uso de múltiples boxes.

        Args:
            fecha_inicio: Inicio del período
            fecha_fin: Fin del período
            box_ids: IDs específicos de boxes (None = todos)
            piso: Filtrar por piso (None = ambos)
            incluir_inactivos: Incluir boxes inactivos

        Returns:
            Comparativa de uso entre boxes
        """
        # Obtener boxes a analizar
        query = self.db.query(Box)

        if box_ids:
            query = query.filter(Box.id.in_(box_ids))

        if piso:
            query = query.filter(Box.piso == piso)

        if not incluir_inactivos:
            query = query.filter(Box.activo == True)

        boxes = query.all()

        # Calcular estadísticas para cada box
        estadisticas_boxes = []
        for box in boxes:
            stats = self.obtener_estadisticas_box(box.id, fecha_inicio, fecha_fin)
            estadisticas_boxes.append(stats)

        # Calcular promedios por piso
        stats_piso_1 = [s for s in estadisticas_boxes if s.piso == 1]
        stats_piso_2 = [s for s in estadisticas_boxes if s.piso == 2]

        porcentaje_piso_1 = (
            sum(s.porcentaje_uso_promedio for s in stats_piso_1) / len(stats_piso_1)
            if stats_piso_1 else 0
        )

        porcentaje_piso_2 = (
            sum(s.porcentaje_uso_promedio for s in stats_piso_2) / len(stats_piso_2)
            if stats_piso_2 else 0
        )

        # Actualizar uso_piso en cada estadística
        for stats in estadisticas_boxes:
            if stats.piso == 1:
                stats.uso_piso = round(porcentaje_piso_1, 2)
            else:
                stats.uso_piso = round(porcentaje_piso_2, 2)

        # Encontrar box con mayor y menor uso
        box_mayor_uso = max(estadisticas_boxes, key=lambda x: x.porcentaje_uso_promedio) if estadisticas_boxes else None
        box_menor_uso = min(estadisticas_boxes, key=lambda x: x.porcentaje_uso_promedio) if estadisticas_boxes else None

        return ComparativaBoxesDTO(
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            estadisticas_boxes=estadisticas_boxes,
            porcentaje_uso_piso_1=round(porcentaje_piso_1, 2),
            porcentaje_uso_piso_2=round(porcentaje_piso_2, 2),
            box_mayor_uso=box_mayor_uso,
            box_menor_uso=box_menor_uso
        )

    def registrar_cambio_box(
        self,
        box_id: UUID,
        campo: str,
        valor_anterior: Optional[str],
        valor_nuevo: str,
        usuario_id: UUID,
        motivo: Optional[str] = None
    ) -> HistorialBox:
        """
        Registra un cambio en las características de un box.

        Args:
            box_id: ID del box modificado
            campo: Campo que fue modificado
            valor_anterior: Valor anterior del campo
            valor_nuevo: Nuevo valor del campo
            usuario_id: ID del usuario que hizo el cambio
            motivo: Motivo del cambio

        Returns:
            Registro de historial creado
        """
        historial = HistorialBox(
            box_id=box_id,
            campo_modificado=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            motivo=motivo,
            modificado_por=usuario_id
        )

        from app.infraestructura.db.models import HistorialBoxModel
        model = HistorialBoxModel(
            id=historial.id,
            box_id=historial.box_id,
            campo_modificado=historial.campo_modificado,
            valor_anterior=historial.valor_anterior,
            valor_nuevo=historial.valor_nuevo,
            motivo=historial.motivo,
            modificado_por=historial.modificado_por,
            timestamp=historial.timestamp
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return historial

    def obtener_historial_box(
        self,
        box_id: UUID,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None
    ) -> List[HistorialBoxDTO]:
        """
        Obtiene el historial de cambios de un box.

        Args:
            box_id: ID del box
            fecha_inicio: Filtrar desde esta fecha (opcional)
            fecha_fin: Filtrar hasta esta fecha (opcional)

        Returns:
            Lista de cambios del box
        """
        from app.infraestructura.db.models import HistorialBoxModel

        query = self.db.query(HistorialBoxModel).filter(
            HistorialBoxModel.box_id == box_id
        )

        if fecha_inicio:
            query = query.filter(HistorialBoxModel.timestamp >= fecha_inicio)

        if fecha_fin:
            query = query.filter(HistorialBoxModel.timestamp <= fecha_fin)

        historiales = query.order_by(HistorialBoxModel.timestamp.desc()).all()

        return [HistorialBoxDTO.model_validate(h) for h in historiales]
