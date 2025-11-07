"""
Ventana de Login
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from controllers.auth_controller import AuthController
from controllers.errors import ErrorHandler, AuthenticationError
from controllers.validators import Validators
from resources.constants import APP_NAME


class LoginWindow(QWidget):
    """Ventana de inicio de sesión"""

    # Señal emitida cuando el login es exitoso
    login_successful = pyqtSignal(dict)  # Emite datos del usuario

    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} - Iniciar Sesión")
        self.setFixedSize(400, 500)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        # Título
        title_label = QLabel(APP_NAME)
        title_label.setProperty("type", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión de Agenda Clínica")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)

        # Frame del formulario
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Campo de usuario
        user_label = QLabel("Usuario:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su nombre de usuario")
        self.username_input.returnPressed.connect(self.handle_login)

        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        # Checkbox recordar sesión
        self.remember_checkbox = QCheckBox("Recordar sesión")

        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setMinimumHeight(40)

        # Link de registro
        register_layout = QHBoxLayout()
        register_label = QLabel("¿No tienes cuenta?")
        self.register_link = QPushButton("Regístrate")
        self.register_link.setProperty("type", "secondary")
        self.register_link.clicked.connect(self.show_register)
        self.register_link.setFlat(True)
        self.register_link.setCursor(Qt.CursorShape.PointingHandCursor)

        register_layout.addWidget(register_label)
        register_layout.addWidget(self.register_link)
        register_layout.addStretch()

        # Añadir widgets al formulario
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addWidget(self.login_button)
        form_layout.addLayout(register_layout)

        form_frame.setLayout(form_layout)

        # Añadir todo al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(form_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def handle_login(self):
        """Maneja el evento de login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        remember_me = self.remember_checkbox.isChecked()

        # Validaciones básicas
        if not username:
            ErrorHandler.show_warning(self, "Validación", "El nombre de usuario es obligatorio")
            self.username_input.setFocus()
            return

        if not password:
            ErrorHandler.show_warning(self, "Validación", "La contraseña es obligatoria")
            self.password_input.setFocus()
            return

        # Deshabilitar botón durante el proceso
        self.login_button.setEnabled(False)
        self.login_button.setText("Iniciando sesión...")

        # Ejecutar login de forma asíncrona
        asyncio.create_task(self._do_login(username, password, remember_me))

    async def _do_login(self, username: str, password: str, remember_me: bool):
        """Ejecuta el login de forma asíncrona"""
        try:
            user_data = await self.auth_controller.login(username, password, remember_me)

            # Emitir señal de éxito
            self.login_successful.emit(user_data)

            # Mostrar mensaje de bienvenida
            ErrorHandler.show_success(
                self,
                "Bienvenido",
                f"¡Bienvenido, {user_data.get('nombre_completo')}!"
            )

        except AuthenticationError as e:
            ErrorHandler.show_error(self, "Error de Autenticación", str(e))
        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            # Rehabilitar botón
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")

    def show_register(self):
        """Muestra la ventana de registro"""
        # Importar aquí para evitar import circular
        from ui.register_window import RegisterWindow

        self.register_window = RegisterWindow()
        self.register_window.registration_successful.connect(self.on_register_success)
        self.register_window.show()

    def on_register_success(self):
        """Maneja el evento de registro exitoso"""
        ErrorHandler.show_info(
            self,
            "Registro Exitoso",
            "Tu cuenta ha sido creada exitosamente.\n"
            "Un administrador debe aprobar tu cuenta antes de que puedas iniciar sesión."
        )

    def clear_form(self):
        """Limpia el formulario"""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.username_input.setFocus()

    async def try_restore_session(self) -> bool:
        """
        Intenta restaurar una sesión guardada

        Returns:
            True si se restauró exitosamente, False en caso contrario
        """
        try:
            if await self.auth_controller.restore_session():
                user_data = self.auth_controller.get_user_info()
                self.login_successful.emit(user_data)
                return True
        except Exception as e:
            print(f"No se pudo restaurar sesión: {e}")

        return False
