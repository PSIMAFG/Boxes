"""
Ventana de gestión de usuarios (solo Admin)
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt

from controllers.api_client import APIClient
from controllers.errors import ErrorHandler
from controllers.role_guard import RoleGuard, Permission
from resources.constants import UserStatus, Roles


class UsuariosWindow(QWidget):
    """Ventana para gestionar usuarios (aprobación, activación/desactivación)"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.role_guard = RoleGuard()
        self.users_data = []
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header con botones
        header_layout = QHBoxLayout()

        info_label = QLabel("Gestión de Usuarios del Sistema")
        info_label.setStyleSheet("font-size: 14px; color: #757575;")

        self.refresh_button = QPushButton("🔄 Actualizar")
        self.refresh_button.clicked.connect(self.load_users)

        header_layout.addWidget(info_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre", "Email", "Rol", "Estado", "Acciones"
        ])

        # Configurar tabla
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Añadir al layout
        layout.addLayout(header_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_users(self):
        """Carga la lista de usuarios"""
        asyncio.create_task(self._do_load_users())

    async def _do_load_users(self):
        """Carga usuarios de forma asíncrona"""
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Cargando...")

            # Obtener usuarios
            users = await self.api_client.get_users()
            self.users_data = users

            # Limpiar tabla
            self.table.setRowCount(0)

            # Llenar tabla
            for user in users:
                self.add_user_row(user)

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("🔄 Actualizar")

    def add_user_row(self, user: dict):
        """Añade una fila con datos de usuario"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # ID
        self.table.setItem(row, 0, QTableWidgetItem(str(user.get("id", ""))))

        # Usuario
        self.table.setItem(row, 1, QTableWidgetItem(user.get("username", "")))

        # Nombre
        self.table.setItem(row, 2, QTableWidgetItem(user.get("nombre_completo", "")))

        # Email
        self.table.setItem(row, 3, QTableWidgetItem(user.get("email", "")))

        # Rol
        role = user.get("role", "")
        role_display = Roles.DISPLAY_NAMES.get(role, role)
        self.table.setItem(row, 4, QTableWidgetItem(role_display))

        # Estado
        estado = user.get("estado", "")
        estado_display = UserStatus.DISPLAY_NAMES.get(estado, estado)
        estado_item = QTableWidgetItem(estado_display)

        if estado == UserStatus.PENDIENTE:
            estado_item.setForeground(Qt.GlobalColor.darkYellow)
        elif estado == UserStatus.APROBADO:
            estado_item.setForeground(Qt.GlobalColor.darkGreen)
        else:
            estado_item.setForeground(Qt.GlobalColor.red)

        self.table.setItem(row, 5, estado_item)

        # Botones de acción
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)

        # Botón aprobar (solo si está pendiente)
        if estado == UserStatus.PENDIENTE and self.role_guard.has_permission(Permission.APPROVE_USER):
            approve_btn = QPushButton("✓ Aprobar")
            approve_btn.setProperty("type", "success")
            approve_btn.clicked.connect(lambda: self.approve_user(user.get("id")))
            actions_layout.addWidget(approve_btn)

        # Botón activar/desactivar
        if self.role_guard.has_permission(Permission.APPROVE_USER):
            is_active = user.get("is_active", True)
            toggle_btn = QPushButton("🔒 Desactivar" if is_active else "🔓 Activar")
            toggle_btn.setProperty("type", "danger" if is_active else "success")
            toggle_btn.clicked.connect(lambda: self.toggle_user(user.get("id")))
            actions_layout.addWidget(toggle_btn)

        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 6, actions_widget)

    def approve_user(self, user_id: int):
        """Aprueba un usuario"""
        if ErrorHandler.confirm(self, "Aprobar Usuario", "¿Está seguro de aprobar este usuario?"):
            asyncio.create_task(self._do_approve_user(user_id))

    async def _do_approve_user(self, user_id: int):
        """Aprueba usuario de forma asíncrona"""
        try:
            await self.api_client.approve_user(user_id)
            ErrorHandler.show_success(self, "Éxito", "Usuario aprobado correctamente")
            await self._do_load_users()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def toggle_user(self, user_id: int):
        """Activa/desactiva un usuario"""
        asyncio.create_task(self._do_toggle_user(user_id))

    async def _do_toggle_user(self, user_id: int):
        """Activa/desactiva usuario de forma asíncrona"""
        try:
            await self.api_client.toggle_user_active(user_id)
            ErrorHandler.show_success(self, "Éxito", "Estado del usuario actualizado")
            await self._do_load_users()
        except Exception as e:
            ErrorHandler.handle_exception(self, e)
