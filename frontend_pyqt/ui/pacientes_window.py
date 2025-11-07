"""
Ventana de gestión de pacientes
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QLineEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from controllers.api_client import APIClient
from controllers.errors import ErrorHandler
from controllers.role_guard import RoleGuard, Permission
from controllers.validators import Validators


class PacienteDialog(QDialog):
    """Diálogo para crear/editar paciente"""

    def __init__(self, parent=None, paciente_data=None):
        super().__init__(parent)
        self.paciente_data = paciente_data
        self.is_edit = paciente_data is not None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Editar Paciente" if self.is_edit else "Nuevo Paciente")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QFormLayout()

        # Nombre
        self.nombre_input = QLineEdit()
        if self.paciente_data:
            self.nombre_input.setText(self.paciente_data.get("nombre", ""))
        form_layout.addRow("Nombre *:", self.nombre_input)

        # RUT
        self.rut_input = QLineEdit()
        if self.paciente_data:
            self.rut_input.setText(self.paciente_data.get("rut", ""))
        form_layout.addRow("RUT *:", self.rut_input)

        # Email
        self.email_input = QLineEdit()
        if self.paciente_data:
            self.email_input.setText(self.paciente_data.get("email", ""))
        form_layout.addRow("Email:", self.email_input)

        # Teléfono
        self.telefono_input = QLineEdit()
        if self.paciente_data:
            self.telefono_input.setText(self.paciente_data.get("telefono", ""))
        form_layout.addRow("Teléfono:", self.telefono_input)

        # Dirección
        self.direccion_input = QLineEdit()
        if self.paciente_data:
            self.direccion_input.setText(self.paciente_data.get("direccion", ""))
        form_layout.addRow("Dirección:", self.direccion_input)

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
        # Validar nombre
        is_valid, error = Validators.validate_required(self.nombre_input.text(), "El nombre")
        if not is_valid:
            ErrorHandler.show_warning(self, "Validación", error)
            return

        # Validar RUT
        is_valid, error = Validators.validate_rut(self.rut_input.text())
        if not is_valid:
            ErrorHandler.show_warning(self, "Validación", error)
            return

        # Validar email si se proporcionó
        email = self.email_input.text().strip()
        if email:
            is_valid, error = Validators.validate_email(email)
            if not is_valid:
                ErrorHandler.show_warning(self, "Validación", error)
                return

        self.accept()

    def get_data(self) -> dict:
        """Obtiene los datos del formulario"""
        return {
            "nombre": self.nombre_input.text().strip(),
            "rut": self.rut_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "telefono": self.telefono_input.text().strip() or None,
            "direccion": self.direccion_input.text().strip() or None,
        }


class PacientesWindow(QWidget):
    """Ventana de gestión de pacientes"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.role_guard = RoleGuard()
        self.pacientes_data = []
        self.init_ui()
        self.load_pacientes()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        info_label = QLabel("Gestión de Pacientes")
        info_label.setStyleSheet("font-size: 14px; color: #757575;")

        # Buscador
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o RUT...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_table)

        self.add_button = QPushButton("➕ Nuevo Paciente")
        self.add_button.setProperty("type", "success")
        self.add_button.clicked.connect(self.add_paciente)

        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.load_pacientes)

        # Aplicar permisos
        self.role_guard.guard_button(self.add_button, Permission.CREATE_PACIENTE, hide=True)

        header_layout.addWidget(info_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.refresh_button)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "RUT", "Email", "Teléfono", "Dirección", "Acciones"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addLayout(header_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_pacientes(self):
        """Carga la lista de pacientes"""
        asyncio.create_task(self._do_load_pacientes())

    async def _do_load_pacientes(self):
        """Carga pacientes de forma asíncrona"""
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Cargando...")

            pacientes = await self.api_client.get_pacientes()
            self.pacientes_data = pacientes

            self.populate_table()

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("🔄 Actualizar")

    def populate_table(self, filtered_data=None):
        """Puebla la tabla con datos"""
        data = filtered_data if filtered_data is not None else self.pacientes_data

        self.table.setRowCount(0)

        for paciente in data:
            self.add_paciente_row(paciente)

    def add_paciente_row(self, paciente: dict):
        """Añade una fila de paciente"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(str(paciente.get("id", ""))))
        self.table.setItem(row, 1, QTableWidgetItem(paciente.get("nombre", "")))
        self.table.setItem(row, 2, QTableWidgetItem(paciente.get("rut", "")))
        self.table.setItem(row, 3, QTableWidgetItem(paciente.get("email", "") or ""))
        self.table.setItem(row, 4, QTableWidgetItem(paciente.get("telefono", "") or ""))
        self.table.setItem(row, 5, QTableWidgetItem(paciente.get("direccion", "") or ""))

        # Botones de acción
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)

        if self.role_guard.has_permission(Permission.EDIT_PACIENTE):
            edit_btn = QPushButton("✏️ Editar")
            edit_btn.clicked.connect(lambda: self.edit_paciente(paciente))
            actions_layout.addWidget(edit_btn)

        if self.role_guard.has_permission(Permission.DELETE_PACIENTE):
            delete_btn = QPushButton("🗑️ Eliminar")
            delete_btn.setProperty("type", "danger")
            delete_btn.clicked.connect(lambda: self.delete_paciente(paciente.get("id")))
            actions_layout.addWidget(delete_btn)

        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 6, actions_widget)

    def filter_table(self, text: str):
        """Filtra la tabla por texto"""
        text = text.lower()
        filtered = [
            p for p in self.pacientes_data
            if text in p.get("nombre", "").lower() or text in p.get("rut", "").lower()
        ]
        self.populate_table(filtered)

    def add_paciente(self):
        """Abre diálogo para añadir paciente"""
        dialog = PacienteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_create_paciente(data))

    async def _do_create_paciente(self, data: dict):
        """Crea paciente de forma asíncrona"""
        try:
            await self.api_client.create_paciente(data)
            ErrorHandler.show_success(self, "Éxito", "Paciente creado correctamente")
            await self._do_load_pacientes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def edit_paciente(self, paciente: dict):
        """Abre diálogo para editar paciente"""
        dialog = PacienteDialog(self, paciente)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            asyncio.create_task(self._do_update_paciente(paciente["id"], data))

    async def _do_update_paciente(self, paciente_id: int, data: dict):
        """Actualiza paciente de forma asíncrona"""
        try:
            await self.api_client.update_paciente(paciente_id, data)
            ErrorHandler.show_success(self, "Éxito", "Paciente actualizado correctamente")
            await self._do_load_pacientes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def delete_paciente(self, paciente_id: int):
        """Elimina un paciente"""
        if ErrorHandler.confirm(self, "Eliminar Paciente", "¿Está seguro de eliminar este paciente?"):
            asyncio.create_task(self._do_delete_paciente(paciente_id))

    async def _do_delete_paciente(self, paciente_id: int):
        """Elimina paciente de forma asíncrona"""
        try:
            await self.api_client.delete_paciente(paciente_id)
            ErrorHandler.show_success(self, "Éxito", "Paciente eliminado correctamente")
            await self._do_load_pacientes()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)
