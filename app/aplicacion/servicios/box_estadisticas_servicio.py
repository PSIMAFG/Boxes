"""
Servicio para cálculo de estadísticas de uso de boxes.
Proporciona simulación y análisis de ocupación de boxes.
"""
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.infraestructura.db.models import BoxModel, CitaModel, EstadoCita
from app.infraestructura.repos.box_repo import BoxRepo


class BoxEstadisticasServicio:
    """Servicio de estadísticas y simulación de uso de boxes"""

    def __init__(self, db: Session):
        self.db = db
        self.box_repo = BoxRepo(db)

    def calcular_uso_por_hora(
        self,
        box_id: Optional[UUID] = None,
        fecha: Optional[date] = None,
        hora_inicio: int = 8,
        hora_fin: int = 20
    ) -> Dict[str, Any]:
        """
        Calcula el uso de boxes por hora.

        Args:
            box_id: ID del box específico (None para todos)
            fecha: Fecha a analizar (None para hoy)
            hora_inicio: Hora de inicio del análisis (default: 8am)
            hora_fin: Hora de fin del análisis (default: 8pm)

        Returns:
            Diccionario con estadísticas por hora
        """
        if fecha is None:
            fecha = date.today()

        # Crear rango de fechas
        fecha_inicio = datetime.combine(fecha, time(hora_inicio, 0))
        fecha_fin_dt = datetime.combine(fecha, time(hora_fin, 0))

        # Filtrar citas
        query = self.db.query(CitaModel).filter(
            CitaModel.inicio >= fecha_inicio,
            CitaModel.inicio < fecha_fin_dt,
            CitaModel.estado.in_([EstadoCita.PROGRAMADA, EstadoCita.CONFIRMADA, EstadoCita.CUMPLIDA])
        )

        if box_id:
            query = query.filter(CitaModel.box_id == box_id)

        citas = query.all()

        # Obtener boxes a analizar
        if box_id:
            boxes = [self.box_repo.obtener_por_id(box_id)]
        else:
            boxes = self.box_repo.listar_activos()

        total_boxes = len(boxes)

        # Calcular ocupación por hora
        estadisticas_por_hora = {}
        for hora in range(hora_inicio, hora_fin):
            hora_inicio_dt = datetime.combine(fecha, time(hora, 0))
            hora_fin_hora = datetime.combine(fecha, time(hora + 1, 0))

            # Contar citas activas en esta hora
            citas_en_hora = [
                c for c in citas
                if c.inicio < hora_fin_hora and c.fin > hora_inicio_dt
            ]

            # Contar boxes únicos ocupados
            boxes_ocupados = len(set(c.box_id for c in citas_en_hora))

            porcentaje_uso = (boxes_ocupados / total_boxes * 100) if total_boxes > 0 else 0

            estadisticas_por_hora[f"{hora:02d}:00"] = {
                "hora": f"{hora:02d}:00",
                "citas": len(citas_en_hora),
                "boxes_ocupados": boxes_ocupados,
                "boxes_disponibles": total_boxes - boxes_ocupados,
                "porcentaje_uso": round(porcentaje_uso, 2),
                "total_boxes": total_boxes
            }

        return {
            "fecha": fecha.isoformat(),
            "box_id": str(box_id) if box_id else "todos",
            "estadisticas": estadisticas_por_hora,
            "resumen": {
                "total_boxes": total_boxes,
                "total_citas": len(citas),
                "hora_mas_ocupada": max(
                    estadisticas_por_hora.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[0] if estadisticas_por_hora else None,
                "hora_menos_ocupada": min(
                    estadisticas_por_hora.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[0] if estadisticas_por_hora else None
            }
        }

    def calcular_uso_por_dia(
        self,
        box_id: Optional[UUID] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula el uso de boxes por día en un rango de fechas.

        Args:
            box_id: ID del box específico (None para todos)
            fecha_inicio: Fecha de inicio (default: hace 7 días)
            fecha_fin: Fecha de fin (default: hoy)

        Returns:
            Diccionario con estadísticas por día
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=7)

        # Obtener boxes a analizar
        if box_id:
            boxes = [self.box_repo.obtener_por_id(box_id)]
        else:
            boxes = self.box_repo.listar_activos()

        total_boxes = len(boxes)

        # Estadísticas por día
        estadisticas_por_dia = {}
        fecha_actual = fecha_inicio

        while fecha_actual <= fecha_fin:
            inicio_dia = datetime.combine(fecha_actual, time(0, 0))
            fin_dia = datetime.combine(fecha_actual, time(23, 59, 59))

            # Filtrar citas del día
            query = self.db.query(CitaModel).filter(
                CitaModel.inicio >= inicio_dia,
                CitaModel.inicio <= fin_dia,
                CitaModel.estado.in_([EstadoCita.PROGRAMADA, EstadoCita.CONFIRMADA, EstadoCita.CUMPLIDA])
            )

            if box_id:
                query = query.filter(CitaModel.box_id == box_id)

            citas = query.all()

            # Calcular minutos de uso total
            minutos_ocupados = sum((c.fin - c.inicio).total_seconds() / 60 for c in citas)

            # Asumiendo jornada de 12 horas (8am - 8pm)
            minutos_disponibles = total_boxes * 12 * 60

            porcentaje_uso = (minutos_ocupados / minutos_disponibles * 100) if minutos_disponibles > 0 else 0

            estadisticas_por_dia[fecha_actual.isoformat()] = {
                "fecha": fecha_actual.isoformat(),
                "dia_semana": fecha_actual.strftime("%A"),
                "citas": len(citas),
                "minutos_ocupados": round(minutos_ocupados, 2),
                "minutos_disponibles": minutos_disponibles,
                "porcentaje_uso": round(porcentaje_uso, 2),
                "total_boxes": total_boxes
            }

            fecha_actual += timedelta(days=1)

        return {
            "box_id": str(box_id) if box_id else "todos",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "estadisticas": estadisticas_por_dia,
            "resumen": {
                "total_boxes": total_boxes,
                "promedio_uso": round(
                    sum(e["porcentaje_uso"] for e in estadisticas_por_dia.values()) / len(estadisticas_por_dia),
                    2
                ) if estadisticas_por_dia else 0,
                "dia_mas_ocupado": max(
                    estadisticas_por_dia.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[1]["fecha"] if estadisticas_por_dia else None,
                "dia_menos_ocupado": min(
                    estadisticas_por_dia.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[1]["fecha"] if estadisticas_por_dia else None
            }
        }

    def calcular_uso_por_semana(
        self,
        box_id: Optional[UUID] = None,
        semanas: int = 4
    ) -> Dict[str, Any]:
        """
        Calcula el uso de boxes por semana.

        Args:
            box_id: ID del box específico (None para todos)
            semanas: Número de semanas hacia atrás a analizar

        Returns:
            Diccionario con estadísticas por semana
        """
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(weeks=semanas)

        # Obtener boxes a analizar
        if box_id:
            boxes = [self.box_repo.obtener_por_id(box_id)]
        else:
            boxes = self.box_repo.listar_activos()

        total_boxes = len(boxes)

        # Estadísticas por semana
        estadisticas_por_semana = {}
        fecha_actual = fecha_inicio

        semana_num = 1
        while fecha_actual < fecha_fin:
            inicio_semana = fecha_actual
            fin_semana = fecha_actual + timedelta(days=6)

            inicio_semana_dt = datetime.combine(inicio_semana, time(0, 0))
            fin_semana_dt = datetime.combine(fin_semana, time(23, 59, 59))

            # Filtrar citas de la semana
            query = self.db.query(CitaModel).filter(
                CitaModel.inicio >= inicio_semana_dt,
                CitaModel.inicio <= fin_semana_dt,
                CitaModel.estado.in_([EstadoCita.PROGRAMADA, EstadoCita.CONFIRMADA, EstadoCita.CUMPLIDA])
            )

            if box_id:
                query = query.filter(CitaModel.box_id == box_id)

            citas = query.all()

            # Calcular minutos de uso total
            minutos_ocupados = sum((c.fin - c.inicio).total_seconds() / 60 for c in citas)

            # Asumiendo jornada de 12 horas x 5 días laborables
            minutos_disponibles = total_boxes * 12 * 60 * 5

            porcentaje_uso = (minutos_ocupados / minutos_disponibles * 100) if minutos_disponibles > 0 else 0

            semana_label = f"Semana {semana_num} ({inicio_semana.isoformat()} - {fin_semana.isoformat()})"

            estadisticas_por_semana[semana_label] = {
                "semana": semana_num,
                "fecha_inicio": inicio_semana.isoformat(),
                "fecha_fin": fin_semana.isoformat(),
                "citas": len(citas),
                "minutos_ocupados": round(minutos_ocupados, 2),
                "minutos_disponibles": minutos_disponibles,
                "porcentaje_uso": round(porcentaje_uso, 2),
                "total_boxes": total_boxes
            }

            fecha_actual += timedelta(days=7)
            semana_num += 1

        return {
            "box_id": str(box_id) if box_id else "todos",
            "semanas_analizadas": semanas,
            "estadisticas": estadisticas_por_semana,
            "resumen": {
                "total_boxes": total_boxes,
                "promedio_uso": round(
                    sum(e["porcentaje_uso"] for e in estadisticas_por_semana.values()) / len(estadisticas_por_semana),
                    2
                ) if estadisticas_por_semana else 0,
                "semana_mas_ocupada": max(
                    estadisticas_por_semana.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[0] if estadisticas_por_semana else None,
                "semana_menos_ocupada": min(
                    estadisticas_por_semana.items(),
                    key=lambda x: x[1]["porcentaje_uso"]
                )[0] if estadisticas_por_semana else None
            }
        }

    def obtener_estadisticas_por_piso(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de uso agrupadas por piso.

        Returns:
            Diccionario con estadísticas por piso
        """
        boxes = self.box_repo.listar_activos()

        estadisticas_por_piso = {
            "piso_1": {"total_boxes": 0, "boxes": []},
            "piso_2": {"total_boxes": 0, "boxes": []},
            "sin_asignar": {"total_boxes": 0, "boxes": []}
        }

        for box in boxes:
            box_data = {
                "id": str(box.id),
                "nombre": box.nombre,
                "ubicacion": box.ubicacion,
                "capacidad": box.capacidad,
                "equipamiento": box.equipamiento,
                "caracteristicas": box.caracteristicas
            }

            if box.piso == 1:
                estadisticas_por_piso["piso_1"]["total_boxes"] += 1
                estadisticas_por_piso["piso_1"]["boxes"].append(box_data)
            elif box.piso == 2:
                estadisticas_por_piso["piso_2"]["total_boxes"] += 1
                estadisticas_por_piso["piso_2"]["boxes"].append(box_data)
            else:
                estadisticas_por_piso["sin_asignar"]["total_boxes"] += 1
                estadisticas_por_piso["sin_asignar"]["boxes"].append(box_data)

        # Calcular uso actual por piso
        hoy = date.today()
        ahora = datetime.now()

        for piso_key in ["piso_1", "piso_2", "sin_asignar"]:
            piso_data = estadisticas_por_piso[piso_key]
            box_ids = [b["id"] for b in piso_data["boxes"]]

            if box_ids:
                # Contar citas activas ahora
                citas_activas = self.db.query(CitaModel).filter(
                    CitaModel.box_id.in_(box_ids),
                    CitaModel.inicio <= ahora,
                    CitaModel.fin > ahora,
                    CitaModel.estado.in_([EstadoCita.PROGRAMADA, EstadoCita.CONFIRMADA, EstadoCita.CUMPLIDA])
                ).count()

                porcentaje_ocupacion = (citas_activas / piso_data["total_boxes"] * 100) if piso_data["total_boxes"] > 0 else 0

                piso_data["ocupacion_actual"] = {
                    "boxes_ocupados": citas_activas,
                    "boxes_disponibles": piso_data["total_boxes"] - citas_activas,
                    "porcentaje": round(porcentaje_ocupacion, 2)
                }

        return {
            "timestamp": ahora.isoformat(),
            "estadisticas": estadisticas_por_piso,
            "resumen": {
                "total_boxes": sum(p["total_boxes"] for p in estadisticas_por_piso.values()),
                "boxes_piso_1": estadisticas_por_piso["piso_1"]["total_boxes"],
                "boxes_piso_2": estadisticas_por_piso["piso_2"]["total_boxes"],
                "boxes_sin_asignar": estadisticas_por_piso["sin_asignar"]["total_boxes"]
            }
        }

    def simular_ocupacion_futura(
        self,
        dias_adelante: int = 7,
        box_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Simula la ocupación futura de boxes basada en citas programadas.

        Args:
            dias_adelante: Días hacia adelante a simular
            box_id: ID del box específico (None para todos)

        Returns:
            Diccionario con proyección de ocupación
        """
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=dias_adelante)

        # Reutilizar el método de uso por día
        return self.calcular_uso_por_dia(box_id, fecha_inicio, fecha_fin)
