"""
Ventana de Registro de Usuario
"""
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from controllers.auth_controller import AuthController
from controllers.errors import ErrorHandler
from controllers.validators import Validators
from resources.constants import APP_NAME, Roles


class RegisterWindow(QWidget):
    """Ventana de registro de nuevos usuarios"""

    # Señal emitida cuando el registro es exitoso
    registration_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} - Registro de Usuario")
        self.setFixedSize(500, 700)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Título
        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setProperty("type", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)

        # Scroll area para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Widget contenedor del formulario
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # Campos del formulario
        # Nombre completo
        name_label = QLabel("Nombre Completo *")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Juan Pérez González")

        # RUT
        rut_label = QLabel("RUT *")
        self.rut_input = QLineEdit()
        self.rut_input.setPlaceholderText("Ej: 12.345.678-9")
        self.rut_input.textChanged.connect(self.on_rut_changed)
        self.rut_error_label = QLabel("")
        self.rut_error_label.setProperty("type", "error")
        self.rut_error_label.hide()

        # Email
        email_label = QLabel("Email *")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ejemplo@correo.com")
        self.email_error_label = QLabel("")
        self.email_error_label.setProperty("type", "error")
        self.email_error_label.hide()

        # Teléfono
        phone_label = QLabel("Teléfono")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Ej: +56912345678")

        # Usuario
        username_label = QLabel("Nombre de Usuario *")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Mínimo 3 caracteres")
        self.username_error_label = QLabel("")
        self.username_error_label.setProperty("type", "error")
        self.username_error_label.hide()

        # Contraseña
        password_label = QLabel("Contraseña *")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Mínimo 8 caracteres")
        self.password_error_label = QLabel("")
        self.password_error_label.setProperty("type", "error")
        self.password_error_label.hide()

        # Confirmar contraseña
        confirm_label = QLabel("Confirmar Contraseña *")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_error_label = QLabel("")
        self.confirm_error_label.setProperty("type", "error")
        self.confirm_error_label.hide()

        # Rol
        role_label = QLabel("Rol *")
        self.role_combo = QComboBox()
        self.role_combo.addItem("Seleccione un rol", "")
        self.role_combo.addItem(Roles.DISPLAY_NAMES[Roles.PROFESIONAL], Roles.PROFESIONAL)
        self.role_combo.addItem(Roles.DISPLAY_NAMES[Roles.ADMINISTRATIVO], Roles.ADMINISTRATIVO)

        # Nota sobre aprobación
        info_label = QLabel(
            "⚠️ Nota: Tu cuenta requerirá aprobación de un administrador antes de poder acceder al sistema."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #FF9800; padding: 10px; background-color: #FFF3E0; border-radius: 4px;")

        # Botones
        button_layout = QHBoxLayout()

        self.register_button = QPushButton("Registrarse")
        self.register_button.setProperty("type", "success")
        self.register_button.clicked.connect(self.handle_register)
        self.register_button.setMinimumHeight(40)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setProperty("type", "secondary")
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setMinimumHeight(40)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.register_button)

        # Añadir campos al formulario
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(rut_label)
        form_layout.addWidget(self.rut_input)
        form_layout.addWidget(self.rut_error_label)

        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.email_error_label)

        form_layout.addWidget(phone_label)
        form_layout.addWidget(self.phone_input)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.username_error_label)

        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.password_error_label)

        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_input)
        form_layout.addWidget(self.confirm_error_label)

        form_layout.addWidget(role_label)
        form_layout.addWidget(self.role_combo)

        form_layout.addWidget(info_label)
        form_layout.addLayout(button_layout)

        form_widget.setLayout(form_layout)
        scroll.setWidget(form_widget)

        # Añadir todo al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def on_rut_changed(self, text: str):
        """Valida el RUT mientras se escribe"""
        if len(text) >= 9:  # Longitud mínima para validar
            is_valid, error_msg = Validators.validate_rut(text)
            if not is_valid:
                self.rut_error_label.setText(error_msg)
                self.rut_error_label.show()
            else:
                self.rut_error_label.hide()
                # Formatear automáticamente
                formatted = Validators.format_rut(text)
                if formatted != text:
                    self.rut_input.setText(formatted)

    def validate_form(self) -> bool:
        """
        Valida todos los campos del formulario

        Returns:
            True si es válido, False en caso contrario
        """
        is_valid = True

        # Validar nombre
        is_valid_name, name_error = Validators.validate_required(
            self.name_input.text(),
            "El nombre completo"
        )
        if not is_valid_name:
            ErrorHandler.show_warning(self, "Validación", name_error)
            self.name_input.setFocus()
            return False

        # Validar RUT
        is_valid_rut, rut_error = Validators.validate_rut(self.rut_input.text())
        if not is_valid_rut:
            self.rut_error_label.setText(rut_error)
            self.rut_error_label.show()
            self.rut_input.setFocus()
            return False

        # Validar email
        is_valid_email, email_error = Validators.validate_email(self.email_input.text())
        if not is_valid_email:
            self.email_error_label.setText(email_error)
            self.email_error_label.show()
            self.email_input.setFocus()
            return False

        # Validar teléfono (opcional)
        phone = self.phone_input.text().strip()
        if phone:
            is_valid_phone, phone_error = Validators.validate_phone(phone)
            if not is_valid_phone:
                ErrorHandler.show_warning(self, "Validación", phone_error)
                self.phone_input.setFocus()
                return False

        # Validar username
        is_valid_username, username_error = Validators.validate_username(self.username_input.text())
        if not is_valid_username:
            self.username_error_label.setText(username_error)
            self.username_error_label.show()
            self.username_input.setFocus()
            return False

        # Validar contraseña
        is_valid_password, password_error = Validators.validate_password(self.password_input.text())
        if not is_valid_password:
            self.password_error_label.setText(password_error)
            self.password_error_label.show()
            self.password_input.setFocus()
            return False

        # Validar que las contraseñas coincidan
        if self.password_input.text() != self.confirm_input.text():
            self.confirm_error_label.setText("Las contraseñas no coinciden")
            self.confirm_error_label.show()
            self.confirm_input.setFocus()
            return False

        # Validar rol
        if not self.role_combo.currentData():
            ErrorHandler.show_warning(self, "Validación", "Debe seleccionar un rol")
            self.role_combo.setFocus()
            return False

        return True

    def handle_register(self):
        """Maneja el evento de registro"""
        # Validar formulario
        if not self.validate_form():
            return

        # Deshabilitar botón durante el proceso
        self.register_button.setEnabled(False)
        self.register_button.setText("Registrando...")

        # Ejecutar registro de forma asíncrona
        asyncio.create_task(self._do_register())

    async def _do_register(self):
        """Ejecuta el registro de forma asíncrona"""
        try:
            # Preparar datos
            username = self.username_input.text().strip()
            password = self.password_input.text()
            email = self.email_input.text().strip()
            nombre_completo = self.name_input.text().strip()
            rut = self.rut_input.text().strip()
            role = self.role_combo.currentData()
            telefono = self.phone_input.text().strip() or None

            # Registrar usuario
            user_data = await self.auth_controller.register(
                username=username,
                password=password,
                email=email,
                nombre_completo=nombre_completo,
                rut=rut,
                role=role,
                telefono=telefono
            )

            # Emitir señal de éxito
            self.registration_successful.emit()

            # Cerrar ventana
            self.close()

        except Exception as e:
            ErrorHandler.handle_exception(self, e)
        finally:
            # Rehabilitar botón
            self.register_button.setEnabled(True)
            self.register_button.setText("Registrarse")
