"""
Ventana de perfil de usuario
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controllers.user_state import UserState
from controllers.auth_controller import AuthController
from controllers.api_client import APIClient
from controllers.errors import ErrorHandler
from controllers.validators import Validators
from resources.constants import Roles


class PerfilWindow(QWidget):
    """Ventana de perfil del usuario"""

    def __init__(self):
        super().__init__()
        self.user_state = UserState()
        self.auth_controller = AuthController()
        self.api_client = APIClient()
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        title_label = QLabel("Mi Perfil")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)

        # Frame de información personal
        info_group = QGroupBox("Información Personal")
        info_layout = QFormLayout()

        # Campos de solo lectura
        self.username_label = QLabel(self.user_state.username or "")
        self.username_label.setStyleSheet("font-weight: bold;")

        self.role_label = QLabel(
            Roles.DISPLAY_NAMES.get(self.user_state.role, self.user_state.role)
        )
        self.role_label.setStyleSheet("color: #2196F3; font-weight: bold;")

        self.user_id_label = QLabel(str(self.user_state.user_id or ""))

        # Campos editables
        self.nombre_input = QLineEdit()
        self.nombre_input.setText(self.user_state.nombre_completo or "")

        self.email_input = QLineEdit()
        self.email_input.setText(self.user_state.email or "")

        # Añadir campos al formulario
        info_layout.addRow("ID de Usuario:", self.user_id_label)
        info_layout.addRow("Usuario:", self.username_label)
        info_layout.addRow("Rol:", self.role_label)
        info_layout.addRow("Nombre Completo:", self.nombre_input)
        info_layout.addRow("Email:", self.email_input)

        info_group.setLayout(info_layout)

        # Frame de cambio de contraseña
        password_group = QGroupBox("Cambiar Contraseña")
        password_layout = QFormLayout()

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setPlaceholderText("Contraseña actual")

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Nueva contraseña (mín. 8 caracteres)")

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirmar nueva contraseña")

        password_layout.addRow("Contraseña Actual:", self.current_password_input)
        password_layout.addRow("Nueva Contraseña:", self.new_password_input)
        password_layout.addRow("Confirmar Contraseña:", self.confirm_password_input)

        password_group.setLayout(password_layout)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("💾 Guardar Cambios")
        self.save_button.setProperty("type", "success")
        self.save_button.clicked.connect(self.save_changes)

        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.setProperty("type", "secondary")
        self.cancel_button.clicked.connect(self.load_user_data)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        # Info adicional
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        info_content_layout = QVBoxLayout()
        info_title = QLabel("ℹ️ Información")
        info_title.setStyleSheet("font-weight: bold; color: #1976D2;")

        info_text = QLabel(
            "• Los cambios en tu información personal se guardarán en tu perfil.\n"
            "• Para cambiar tu contraseña, debes ingresar tu contraseña actual.\n"
            "• La nueva contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #1976D2; font-size: 11px;")

        info_content_layout.addWidget(info_title)
        info_content_layout.addWidget(info_text)
        info_frame.setLayout(info_content_layout)

        # Añadir todo al layout principal
        layout.addWidget(title_label)
        layout.addWidget(info_group)
        layout.addWidget(password_group)
        layout.addWidget(info_frame)
        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.setLayout(layout)

    def load_user_data(self):
        """Carga los datos del usuario"""
        asyncio.create_task(self._do_load_user_data())

    async def _do_load_user_data(self):
        """Carga datos del usuario de forma asíncrona"""
        try:
            user_data = await self.auth_controller.get_current_user()

            # Actualizar campos
            self.nombre_input.setText(user_data.get("nombre_completo", ""))
            self.email_input.setText(user_data.get("email", ""))

            # Limpiar campos de contraseña
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()

        except Exception as e:
            ErrorHandler.handle_exception(self, e)

    def save_changes(self):
        """Guarda los cambios del perfil"""
        # Validar campos
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()

        is_valid, error = Validators.validate_required(nombre, "El nombre")
        if not is_valid:
            ErrorHandler.show_warning(self, "Validación", error)
            return

        is_valid, error = Validators.validate_email(email)
        if not is_valid:
            ErrorHandler.show_warning(self, "Validación", error)
            return

        # Verificar si hay cambio de contraseña
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if any([current_password, new_password, confirm_password]):
            # Validar cambio de contraseña
            if not all([current_password, new_password, confirm_password]):
                ErrorHandler.show_warning(
                    self,
                    "Validación",
                    "Para cambiar la contraseña, debes completar todos los campos de contraseña"
                )
                return

            is_valid, error = Validators.validate_password(new_password)
            if not is_valid:
                ErrorHandler.show_warning(self, "Validación", error)
                return

            if new_password != confirm_password:
                ErrorHandler.show_warning(
                    self,
                    "Validación",
                    "La nueva contraseña y su confirmación no coinciden"
                )
                return

        # Guardar cambios
        asyncio.create_task(self._do_save_changes(nombre, email, new_password if new_password else None))

    async def _do_save_changes(self, nombre: str, email: str, new_password: str = None):
        """Guarda cambios de forma asíncrona"""
        try:
            self.save_button.setEnabled(False)
            self.save_button.setText("Guardando...")

            # Preparar datos
            update_data = {
                "nombre_completo": nombre,
                "email": email,
            }

            if new_password:
                update_data["password"] = new_password

            # Actualizar en el backend
            await self.api_client.update_user(self.user_state.user_id, update_data)

            # Actualizar estado local
            self.user_state._nombre_completo = nombre
            self.user_state._email = email

            ErrorHandler.show_success(
                self,
                "Éxito",
                "Tu perfil ha sido actualizado correctamente"
            )

            # Recargar datos
            await self._do_load_user_data()

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            self.save_button.setEnabled(True)
            self.save_button.setText("💾 Guardar Cambios")
