"""
Ventana principal del Dashboard con navegación por roles
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QStackedWidget,
    QFrame, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from controllers.user_state import UserState
from controllers.role_guard import RoleGuard, Permission
from controllers.navigation import NavigationController
from controllers.auth_controller import AuthController
from resources.constants import APP_NAME, Roles


class DashboardWindow(QMainWindow):
    """Ventana principal del dashboard con navegación"""

    # Señal para cerrar sesión
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.user_state = UserState()
        self.role_guard = RoleGuard()
        self.auth_controller = AuthController()

        self.init_ui()
        self.setup_navigation()
        self.apply_role_permissions()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} - Dashboard")
        self.setMinimumSize(1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel lateral izquierdo (navegación)
        self.sidebar = self.create_sidebar()

        # Panel derecho (contenido)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        self.header = self.create_header()

        # Stacked widget para las diferentes vistas
        self.stacked_widget = QStackedWidget()

        content_layout.addWidget(self.header)
        content_layout.addWidget(self.stacked_widget)

        content_widget.setLayout(content_layout)

        # Añadir sidebar y contenido
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_widget, 1)  # El contenido se expande

        central_widget.setLayout(main_layout)

    def create_sidebar(self) -> QWidget:
        """Crea el panel lateral de navegación"""
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2196F3;
                border-right: 1px solid #1976D2;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo/Título
        logo_widget = QWidget()
        logo_widget.setFixedHeight(80)
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_label = QLabel("AGENDA")
        app_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(app_label)
        logo_widget.setLayout(logo_layout)

        # Lista de navegación
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: #1976D2;
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)

        # Información del usuario en la parte inferior
        user_widget = self.create_user_info_widget()

        layout.addWidget(logo_widget)
        layout.addWidget(self.nav_list)
        layout.addStretch()
        layout.addWidget(user_widget)

        sidebar.setLayout(layout)
        return sidebar

    def create_user_info_widget(self) -> QWidget:
        """Crea el widget de información del usuario"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border-top: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)

        # Nombre de usuario
        self.user_name_label = QLabel(self.user_state.nombre_completo or "Usuario")
        self.user_name_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        self.user_name_label.setWordWrap(True)

        # Rol
        role_display = Roles.DISPLAY_NAMES.get(self.user_state.role, self.user_state.role)
        self.user_role_label = QLabel(role_display)
        self.user_role_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 10px;")

        # Botón de cerrar sesión
        self.logout_button = QPushButton("Cerrar Sesión")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.logout_button.clicked.connect(self.handle_logout)

        layout.addWidget(self.user_name_label)
        layout.addWidget(self.user_role_label)
        layout.addSpacing(10)
        layout.addWidget(self.logout_button)

        widget.setLayout(layout)
        return widget

    def create_header(self) -> QWidget:
        """Crea el header superior"""
        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #E0E0E0;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)

        # Título de la sección actual
        self.section_title = QLabel("Inicio")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.section_title.setFont(font)

        layout.addWidget(self.section_title)
        layout.addStretch()

        header.setLayout(layout)
        return header

    def setup_navigation(self):
        """Configura la navegación y las páginas"""
        # Crear controlador de navegación
        self.navigation = NavigationController(self.stacked_widget)

        # Importar ventanas dinámicamente para evitar imports circulares
        from ui.inicio_view import InicioView
        from ui.perfil_window import PerfilWindow

        # Añadir páginas base
        inicio_view = InicioView()
        perfil_view = PerfilWindow()

        self.navigation.add_page("Inicio", inicio_view)
        self.navigation.add_page("Perfil", perfil_view)

        # Añadir items de navegación base
        self.add_nav_item("🏠 Inicio", "Inicio")
        self.add_nav_item("👤 Perfil", "Perfil")

        # Añadir páginas según permisos
        if self.role_guard.has_permission(Permission.VIEW_USERS):
            from ui.usuarios_window import UsuariosWindow
            usuarios_view = UsuariosWindow()
            self.navigation.add_page("Usuarios", usuarios_view)
            self.add_nav_item("👥 Usuarios", "Usuarios")

        if self.role_guard.has_permission(Permission.VIEW_PACIENTES):
            from ui.pacientes_window import PacientesWindow
            pacientes_view = PacientesWindow()
            self.navigation.add_page("Pacientes", pacientes_view)
            self.add_nav_item("🏥 Pacientes", "Pacientes")

        if self.role_guard.has_permission(Permission.VIEW_BOXES):
            from ui.boxes_window import BoxesWindow
            boxes_view = BoxesWindow()
            self.navigation.add_page("Boxes", boxes_view)
            self.add_nav_item("📦 Boxes", "Boxes")

        if self.role_guard.has_any_permission([Permission.VIEW_ATENCIONES, Permission.VIEW_OWN_ATENCIONES]):
            from ui.atenciones_window import AtencionesWindow
            atenciones_view = AtencionesWindow()
            self.navigation.add_page("Atenciones", atenciones_view)
            self.add_nav_item("📋 Atenciones", "Atenciones")

        if self.role_guard.has_permission(Permission.VIEW_REPORTES):
            from ui.reportes_window import ReportesWindow
            reportes_view = ReportesWindow()
            self.navigation.add_page("Reportes", reportes_view)
            self.add_nav_item("📊 Reportes", "Reportes")

        # Seleccionar la primera página
        self.nav_list.setCurrentRow(0)

    def add_nav_item(self, text: str, page_name: str):
        """Añade un item de navegación"""
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, page_name)
        self.nav_list.addItem(item)

    def on_nav_changed(self, index: int):
        """Maneja el cambio de navegación"""
        if index < 0:
            return

        item = self.nav_list.item(index)
        page_name = item.data(Qt.ItemDataRole.UserRole)

        # Actualizar título
        self.section_title.setText(page_name)

        # Navegar a la página
        self.navigation.navigate_to(page_name, add_to_history=False)

    def apply_role_permissions(self):
        """Aplica permisos basados en el rol del usuario"""
        # Los permisos ya se aplican en setup_navigation al crear las páginas
        pass

    def handle_logout(self):
        """Maneja el cierre de sesión"""
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            import asyncio
            asyncio.create_task(self._do_logout())

    async def _do_logout(self):
        """Ejecuta el logout de forma asíncrona"""
        await self.auth_controller.logout()
        self.logout_requested.emit()
        self.close()
