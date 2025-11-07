"""
Ventana de reportes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controllers.user_state import UserState
from controllers.role_guard import RoleGuard, Permission


class ReportCard(QFrame):
    """Tarjeta de reporte"""

    def __init__(self, title: str, description: str, icon: str = "📊"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 20px;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
                background-color: #F5F9FF;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()

        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Descripción
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: #757575;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()

        self.setLayout(layout)


class ReportesWindow(QWidget):
    """Ventana de reportes del sistema"""

    def __init__(self):
        super().__init__()
        self.user_state = UserState()
        self.role_guard = RoleGuard()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título
        title_label = QLabel("Reportes y Estadísticas")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title_label.setFont(font)

        # Descripción
        desc_label = QLabel(
            "Selecciona el tipo de reporte que deseas generar. "
            "Los reportes disponibles dependen de tu rol en el sistema."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #757575; font-size: 12px;")

        # Grid de reportes
        reports_grid = QGridLayout()
        reports_grid.setSpacing(15)

        row, col = 0, 0

        # Reportes según permisos
        if self.role_guard.has_permission(Permission.VIEW_REPORTES_GENERALES):
            # Reporte general
            general_card = ReportCard(
                "Reporte General",
                "Estadísticas globales del sistema: usuarios, pacientes, atenciones.",
                "📈"
            )
            general_card.mousePressEvent = lambda e: self.show_general_report()
            reports_grid.addWidget(general_card, row, col)
            col += 1

            # Reporte de atenciones
            atenciones_card = ReportCard(
                "Atenciones por Período",
                "Reporte de atenciones realizadas en un período de tiempo.",
                "📋"
            )
            reports_grid.addWidget(atenciones_card, row, col)
            col += 1

            # Reporte de pacientes
            pacientes_card = ReportCard(
                "Pacientes Activos",
                "Listado y estadísticas de pacientes registrados.",
                "🏥"
            )
            reports_grid.addWidget(pacientes_card, row, col)
            col += 1

            if col >= 3:
                row += 1
                col = 0

        # Reportes personales (para profesionales)
        if self.role_guard.is_profesional():
            mis_atenciones_card = ReportCard(
                "Mis Atenciones",
                "Reporte de tus atenciones realizadas.",
                "👤"
            )
            reports_grid.addWidget(mis_atenciones_card, row, col)
            col += 1

            mis_pacientes_card = ReportCard(
                "Mis Pacientes",
                "Listado de pacientes que has atendido.",
                "📝"
            )
            reports_grid.addWidget(mis_pacientes_card, row, col)

        # Placeholder info
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border: 1px solid #FFB74D;
                border-radius: 8px;
                padding: 20px;
            }
        """)

        info_layout = QVBoxLayout()
        info_title = QLabel("ℹ️ Funcionalidad en Desarrollo")
        info_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F57C00;")

        info_text = QLabel(
            "La generación de reportes completos está en desarrollo. "
            "Próximamente podrás exportar reportes en PDF, Excel y otros formatos."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #F57C00; font-size: 12px;")

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        info_frame.setLayout(info_layout)

        # Añadir al layout principal
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addSpacing(10)
        layout.addLayout(reports_grid)
        layout.addWidget(info_frame)
        layout.addStretch()

        self.setLayout(layout)

    def show_general_report(self):
        """Muestra el reporte general (placeholder)"""
        from controllers.errors import ErrorHandler
        ErrorHandler.show_info(
            self,
            "Reporte General",
            "Esta funcionalidad está en desarrollo.\n"
            "Pronto podrás ver estadísticas completas del sistema."
        )
