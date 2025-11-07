"""
Vista de Inicio/Home del Dashboard
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controllers.user_state import UserState
from resources.constants import Roles, APP_VERSION


class StatCard(QFrame):
    """Tarjeta de estadística"""

    def __init__(self, title: str, value: str, icon: str = ""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()

        # Icono y valor
        value_layout = QHBoxLayout()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 32px;")
            value_layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2196F3;")
        value_layout.addWidget(value_label)
        value_layout.addStretch()

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #757575;")

        layout.addLayout(value_layout)
        layout.addWidget(title_label)
        layout.addStretch()

        self.setLayout(layout)


class InicioView(QWidget):
    """Vista principal de inicio"""

    def __init__(self):
        super().__init__()
        self.user_state = UserState()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Mensaje de bienvenida
        welcome_label = QLabel(f"¡Bienvenido/a, {self.user_state.nombre_completo}!")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        welcome_label.setFont(font)

        # Subtítulo con rol
        role_display = Roles.DISPLAY_NAMES.get(self.user_state.role, self.user_state.role)
        subtitle_label = QLabel(f"Rol: {role_display}")
        subtitle_label.setStyleSheet("font-size: 14px; color: #757575;")

        # Tarjetas de estadísticas (placeholders)
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        # Placeholder stats
        if self.user_state.is_admin():
            stats_grid.addWidget(StatCard("Usuarios Pendientes", "0", "👥"), 0, 0)
            stats_grid.addWidget(StatCard("Boxes Activos", "0", "📦"), 0, 1)
            stats_grid.addWidget(StatCard("Atenciones Hoy", "0", "📋"), 0, 2)
        elif self.user_state.is_profesional():
            stats_grid.addWidget(StatCard("Mis Atenciones Hoy", "0", "📋"), 0, 0)
            stats_grid.addWidget(StatCard("Pacientes Atendidos", "0", "🏥"), 0, 1)
        else:
            stats_grid.addWidget(StatCard("Atenciones Hoy", "0", "📋"), 0, 0)
            stats_grid.addWidget(StatCard("Pacientes Registrados", "0", "🏥"), 0, 1)

        # Panel de información
        info_panel = QFrame()
        info_panel.setFrameShape(QFrame.Shape.StyledPanel)
        info_panel.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 1px solid #90CAF9;
                border-radius: 8px;
                padding: 20px;
            }
        """)

        info_layout = QVBoxLayout()

        info_title = QLabel("ℹ️ Información del Sistema")
        info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2;")

        info_text = QLabel(
            f"Sistema de Agenda Clínica v{APP_VERSION}\n\n"
            "Este sistema te permite gestionar pacientes, boxes y atenciones clínicas "
            "de manera eficiente y segura.\n\n"
            "Utiliza el menú lateral para navegar entre las diferentes secciones."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #1976D2;")

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        info_panel.setLayout(info_layout)

        # Añadir todo al layout principal
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        layout.addLayout(stats_grid)
        layout.addWidget(info_panel)
        layout.addStretch()

        self.setLayout(layout)
