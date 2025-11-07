"""
Aplicación principal del Sistema de Agenda Clínica - Frontend PyQt6
Punto de entrada de la aplicación
"""
import sys
import asyncio
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from qasync import QEventLoop

from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow
from resources.constants import APP_NAME


class Application:
    """Clase principal de la aplicación"""

    def __init__(self):
        # Crear aplicación Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)

        # Cargar estilos
        self.load_styles()

        # Ventanas
        self.login_window = None
        self.dashboard_window = None

        # Crear event loop asíncrono
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

    def load_styles(self):
        """Carga los estilos QSS"""
        try:
            style_path = Path(__file__).parent / "resources" / "styles.qss"
            if style_path.exists():
                with open(style_path, "r", encoding="utf-8") as f:
                    stylesheet = f.read()
                    self.app.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"Error al cargar estilos: {e}")

    def show_login(self):
        """Muestra la ventana de login"""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)

        # Intentar restaurar sesión
        QTimer.singleShot(100, lambda: asyncio.create_task(self.try_restore_session()))

        self.login_window.show()

    async def try_restore_session(self):
        """Intenta restaurar una sesión guardada"""
        if self.login_window:
            success = await self.login_window.try_restore_session()
            if success:
                print("Sesión restaurada exitosamente")

    def on_login_success(self, user_data: dict):
        """
        Maneja el evento de login exitoso

        Args:
            user_data: Datos del usuario autenticado
        """
        print(f"Login exitoso: {user_data.get('username')}")

        # Cerrar ventana de login
        if self.login_window:
            self.login_window.close()

        # Mostrar dashboard
        self.show_dashboard()

    def show_dashboard(self):
        """Muestra el dashboard principal"""
        self.dashboard_window = DashboardWindow()
        self.dashboard_window.logout_requested.connect(self.on_logout)
        self.dashboard_window.showMaximized()

    def on_logout(self):
        """Maneja el cierre de sesión"""
        print("Cerrando sesión...")

        # Cerrar dashboard
        if self.dashboard_window:
            self.dashboard_window.close()
            self.dashboard_window = None

        # Mostrar login nuevamente
        self.show_login()

    def run(self):
        """Ejecuta la aplicación"""
        self.show_login()

        # Ejecutar event loop
        with self.loop:
            self.loop.run_forever()


def main():
    """Función principal"""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
