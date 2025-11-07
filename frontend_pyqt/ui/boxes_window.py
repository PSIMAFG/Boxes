"""
Ventana de gestión de boxes
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QDialog, QFormLayout, QDialogButtonBox, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt

from controllers.api_client import APIClient
from controllers.errors import ErrorHandler
from controllers.role_guard import RoleGuard, Permission
from controllers.validators import Validators


class BoxDialog(QDialog):
    """Diálogo para crear/editar box"""

    def __init__(self, parent=None, box_data=None):
        super().__init__(parent)
        self.box_data = box_data
        self.is_edit = box_data is not None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Editar Box" if self.is_edit else "Nuevo Box")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QFormLayout()

        # Nombre
        self.nombre_input = QLineEdit()
        if self.box_data:
            self.nombre_input.setText(self.box_data.get("nombre", ""))
        form_layout.addRow("Nombre *:", self.nombre_input)

        # Descripción
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(100)
        if self.box_data:
            self.descripcion_input.setPlainText(self.box_data.get("descripcion", ""))
        form_layout.addRow("Descripción:", self.descripcion_input)

        # Ubicación
        self.ubicacion_input = QLineEdit()
        if self.box_data:
            self.ubicacion_input.setText(self.box_data.get("ubicacion", ""))
        form_layout.addRow("Ubicación:", self.ubicacion_input)

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
        is_valid, error = Validators.validate_required(self.nombre_input.text(), "El nombre")
        if not is_valid:
            ErrorHandler.show_warning(self, "Validación", error)
            return

        self.accept()

    def get_data(self) -> dict:
        """Obtiene los datos del formulario"""
        return {
            "nombre": self.nombre_input.text().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip() or None,
            "ubicacion": self.ubicacion_input.text().strip() or None,
        }


class BoxesWindow(QWidget):
    """Ventana de gestión de boxes"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.role_guard = RoleGuard()
        self.boxes_data = []
        self.init_ui()
        self.load_boxes()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        info_label = QLabel("Gestión de Boxes")
        info_label.setStyleSheet("font-size: 14px; color: #757575;")

        self.add_button = QPushButton("➕ Nuevo Box")
        self.add_button.setProperty("type", "success")
        self.add_button.clicked.connect(self.add_box)

        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.load_boxes)

        # Aplicar permisos
        self.role_guard.guard_button(self.add_button, Permission.CREATE_BOX, hide=True)

        header_layout.addWidget(info_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Ubicación", "Acciones"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addLayout(header_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_boxes(self):
        """Carga la lista de boxes"""
        asyncio.create_task(self._do_load_boxes())

    async def _do_load_boxes(self):
        """Carga boxes de forma asíncrona"""
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Cargando...")

            boxes = await self.api_client.get_boxes()
            self.boxes_data = boxes

            self.table.setRowCount(0)

            for box in boxes:
                self.add_box_row(box)

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("🔄 Actualizar")

    def add_box_row(self, box: dict):
        """Añade una fila de box"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(box.get("id", ""))))
        self.table.setItem(row, 1, QTableWidgetItem(box.get("nombre", "")))
        self.table.setItem(row, 2, QTableWidgetItem(box.get("descripcion", "") or ""))
        self.table.setItem(row, 3, QTableWidgetItem(box.get("ubicacion", "") or ""))

        # Botones de acción
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)

        if self.role_guard.has_permission(Permission.EDIT_BOX):
            edit_btn = QPushButton("✏️ Editar")
            edit_btn.clicked.connect(lambda: self.edit_box(box))
            actions_layout.addWidget(edit_btn)

        if self.role_guard.has_permission(Permission.DELETE_BOX):
            delete_btn = QPushButton("🗑️ Eliminar")
            delete_btn.setProperty("type", "danger")
            delete_btn.clicked.connect(lambda: self.delete_box(box.get("id")))
            actions_layout.addWidget(delete_btn)

        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 4, actions_widget)

    def add_box(self):
        """Abre diálogo para añadir box"""
        dialog = BoxDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_create_box(data))

    async def _do_create_box(self, data: dict):
        """Crea box de forma asíncrona"""
        try:
            await self.api_client.create_box(data)
            ErrorHandler.show_success(self, "Éxito", "Box creado correctamente")
            await self._do_load_boxes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def edit_box(self, box: dict):
        """Abre diálogo para editar box"""
        dialog = BoxDialog(self, box)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_update_box(box["id"], data))

    async def _do_update_box(self, box_id: int, data: dict):
        """Actualiza box de forma asíncrona"""
        try:
            await self.api_client.update_box(box_id, data)
            ErrorHandler.show_success(self, "Éxito", "Box actualizado correctamente")
            await self._do_load_boxes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def delete_box(self, box_id: int):
        """Elimina un box"""
        if ErrorHandler.confirm(self, "Eliminar Box", "¿Está seguro de eliminar este box?"):
            asyncio.create_task(self._do_delete_box(box_id))

    async def _do_delete_box(self, box_id: int):
        """Elimina box de forma asíncrona"""
        try:
            await self.api_client.delete_box(box_id)
            ErrorHandler.show_success(self, "Éxito", "Box eliminado correctamente")
            await self._do_load_boxes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)
