"""
Ventana de gestión de atenciones
"""
import asyncio
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QDialog, QFormLayout, QDialogButtonBox, QComboBox,
    QDateTimeEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDateTime

from controllers.api_client import APIClient
from controllers.errors import ErrorHandler
from controllers.role_guard import RoleGuard, Permission
from controllers.user_state import UserState


class AtencionDialog(QDialog):
    """Diálogo para crear/editar atención"""

    def __init__(self, parent=None, atencion_data=None, pacientes=None, boxes=None):
        super().__init__(parent)
        self.atencion_data = atencion_data
        self.is_edit = atencion_data is not None
        self.pacientes = pacientes or []
        self.boxes = boxes or []
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Editar Atención" if self.is_edit else "Nueva Atención")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QFormLayout()

        # Paciente
        self.paciente_combo = QComboBox()
        self.paciente_combo.addItem("Seleccione un paciente", None)
        for paciente in self.pacientes:
            self.paciente_combo.addItem(
                f"{paciente.get('nombre')} - {paciente.get('rut')}",
                paciente.get("id")
            )
        if self.atencion_data:
            paciente_id = self.atencion_data.get("paciente_id")
            for i in range(self.paciente_combo.count()):
                if self.paciente_combo.itemData(i) == paciente_id:
                    self.paciente_combo.setCurrentIndex(i)
                    break
        form_layout.addRow("Paciente *:", self.paciente_combo)

        # Box
        self.box_combo = QComboBox()
        self.box_combo.addItem("Seleccione un box", None)
        for box in self.boxes:
            self.box_combo.addItem(box.get("nombre"), box.get("id"))
        if self.atencion_data:
            box_id = self.atencion_data.get("box_id")
            for i in range(self.box_combo.count()):
                if self.box_combo.itemData(i) == box_id:
                    self.box_combo.setCurrentIndex(i)
                    break
        form_layout.addRow("Box *:", self.box_combo)

        # Fecha y hora
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
        if self.atencion_data and self.atencion_data.get("fecha_hora"):
            # Parse ISO format datetime
            fecha_str = self.atencion_data.get("fecha_hora")
            dt = QDateTime.fromString(fecha_str, Qt.DateFormat.ISODate)
            self.datetime_edit.setDateTime(dt)
        else:
            self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Fecha y Hora *:", self.datetime_edit)

        # Diagnóstico
        self.diagnostico_input = QTextEdit()
        self.diagnostico_input.setMaximumHeight(100)
        if self.atencion_data:
            self.diagnostico_input.setPlainText(self.atencion_data.get("diagnostico", ""))
        form_layout.addRow("Diagnóstico:", self.diagnostico_input)

        # Tratamiento
        self.tratamiento_input = QTextEdit()
        self.tratamiento_input.setMaximumHeight(100)
        if self.atencion_data:
            self.tratamiento_input.setPlainText(self.atencion_data.get("tratamiento", ""))
        form_layout.addRow("Tratamiento:", self.tratamiento_input)

        # Observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setMaximumHeight(100)
        if self.atencion_data:
            self.observaciones_input.setPlainText(self.atencion_data.get("observaciones", ""))
        form_layout.addRow("Observaciones:", self.observaciones_input)

        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def validate_and_accept(self):
        """Valida y acepta el diálogo"""
        if not self.paciente_combo.currentData():
            ErrorHandler.show_warning(self, "Validación", "Debe seleccionar un paciente")
            return

        if not self.box_combo.currentData():
            ErrorHandler.show_warning(self, "Validación", "Debe seleccionar un box")
            return

        self.accept()

    def get_data(self) -> dict:
        """Obtiene los datos del formulario"""
        # Convertir QDateTime a ISO format string
        dt = self.datetime_edit.dateTime()
        fecha_hora_str = dt.toString(Qt.DateFormat.ISODate)

        return {
            "paciente_id": self.paciente_combo.currentData(),
            "box_id": self.box_combo.currentData(),
            "fecha_hora": fecha_hora_str,
            "diagnostico": self.diagnostico_input.toPlainText().strip() or None,
            "tratamiento": self.tratamiento_input.toPlainText().strip() or None,
            "observaciones": self.observaciones_input.toPlainText().strip() or None,
        }


class AtencionesWindow(QWidget):
    """Ventana de gestión de atenciones"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.role_guard = RoleGuard()
        self.user_state = UserState()
        self.atenciones_data = []
        self.pacientes_data = []
        self.boxes_data = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        info_label = QLabel("Gestión de Atenciones")
        info_label.setStyleSheet("font-size: 14px; color: #757575;")

        self.add_button = QPushButton("➕ Nueva Atención")
        self.add_button.setProperty("type", "success")
        self.add_button.clicked.connect(self.add_atencion)

        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.load_data)

        # Aplicar permisos
        self.role_guard.guard_button(self.add_button, Permission.CREATE_ATENCION, hide=True)

        header_layout.addWidget(info_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Paciente", "Box", "Fecha/Hora", "Profesional", "Diagnóstico", "Tratamiento", "Acciones"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addLayout(header_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        """Carga todos los datos necesarios"""
        asyncio.create_task(self._do_load_data())

    async def _do_load_data(self):
        """Carga datos de forma asíncrona"""
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Cargando...")

            # Cargar atenciones (según rol)
            if self.role_guard.has_permission(Permission.VIEW_ATENCIONES):
                atenciones = await self.api_client.get_atenciones()
            else:
                atenciones = await self.api_client.get_atenciones_profesional()

            self.atenciones_data = atenciones

            # Cargar pacientes y boxes para los diálogos
            self.pacientes_data = await self.api_client.get_pacientes()
            self.boxes_data = await self.api_client.get_boxes()

            self.table.setRowCount(0)

            for atencion in atenciones:
                self.add_atencion_row(atencion)

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("🔄 Actualizar")

    def add_atencion_row(self, atencion: dict):
        """Añade una fila de atención"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(atencion.get("id", ""))))

        # Paciente (puede venir como objeto)
        paciente = atencion.get("paciente", {})
        paciente_nombre = paciente.get("nombre", "") if isinstance(paciente, dict) else ""
        self.table.setItem(row, 1, QTableWidgetItem(paciente_nombre))

        # Box (puede venir como objeto)
        box = atencion.get("box", {})
        box_nombre = box.get("nombre", "") if isinstance(box, dict) else ""
        self.table.setItem(row, 2, QTableWidgetItem(box_nombre))

        # Fecha y hora
        fecha_hora = atencion.get("fecha_hora", "")
        if fecha_hora:
            try:
                dt = datetime.fromisoformat(fecha_hora.replace('Z', '+00:00'))
                fecha_format = dt.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_format = fecha_hora
        else:
            fecha_format = ""
        self.table.setItem(row, 3, QTableWidgetItem(fecha_format))

        # Profesional
        profesional = atencion.get("profesional", {})
        profesional_nombre = profesional.get("nombre_completo", "") if isinstance(profesional, dict) else ""
        self.table.setItem(row, 4, QTableWidgetItem(profesional_nombre))

        self.table.setItem(row, 5, QTableWidgetItem(atencion.get("diagnostico", "") or ""))
        self.table.setItem(row, 6, QTableWidgetItem(atencion.get("tratamiento", "") or ""))

        # Botones de acción
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)

        # Verificar permisos de edición
        can_edit = False
        if self.role_guard.has_permission(Permission.EDIT_ATENCION):
            can_edit = True
        elif self.role_guard.has_permission(Permission.EDIT_OWN_ATENCION):
            # Solo puede editar sus propias atenciones
            profesional_id = atencion.get("profesional_id")
            if profesional_id == self.user_state.user_id:
                can_edit = True

        if can_edit:
            edit_btn = QPushButton("✏️ Editar")
            edit_btn.clicked.connect(lambda: self.edit_atencion(atencion))
            actions_layout.addWidget(edit_btn)

        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 7, actions_widget)

    def add_atencion(self):
        """Abre diálogo para añadir atención"""
        dialog = AtencionDialog(self, pacientes=self.pacientes_data, boxes=self.boxes_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_create_atencion(data))

    async def _do_create_atencion(self, data: dict):
        """Crea atención de forma asíncrona"""
        try:
            await self.api_client.create_atencion(data)
            ErrorHandler.show_success(self, "Éxito", "Atención creada correctamente")
            await self._do_load_data()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def edit_atencion(self, atencion: dict):
        """Abre diálogo para editar atención"""
        dialog = AtencionDialog(self, atencion, self.pacientes_data, self.boxes_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_update_atencion(atencion["id"], data))

    async def _do_update_atencion(self, atencion_id: int, data: dict):
        """Actualiza atención de forma asíncrona"""
        try:
            await self.api_client.update_atencion(atencion_id, data)
            ErrorHandler.show_success(self, "Éxito", "Atención actualizada correctamente")
            await self._do_load_data()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)
