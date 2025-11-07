"""
Sistema de navegación entre ventanas
"""
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QStackedWidget, QWidget


class NavigationController:
    """Controlador de navegación para manejar cambio entre vistas"""

    def __init__(self, stacked_widget: QStackedWidget):
        self.stacked_widget = stacked_widget
        self.pages: Dict[str, int] = {}  # Nombre -> índice
        self.history: list = []  # Historial de navegación

    def add_page(self, name: str, widget: QWidget) -> int:
        """
        Añade una página al stack

        Args:
            name: Nombre identificador de la página
            widget: Widget de la página

        Returns:
            Índice de la página añadida
        """
        index = self.stacked_widget.addWidget(widget)
        self.pages[name] = index
        return index

    def navigate_to(self, page_name: str, add_to_history: bool = True):
        """
        Navega a una página específica

        Args:
            page_name: Nombre de la página
            add_to_history: Si agregar al historial
        """
        if page_name not in self.pages:
            print(f"Página '{page_name}' no encontrada")
            return

        index = self.pages[page_name]
        current_index = self.stacked_widget.currentIndex()

        # Añadir a historial si es diferente de la página actual
        if add_to_history and current_index != index:
            self.history.append(current_index)

        self.stacked_widget.setCurrentIndex(index)

    def navigate_to_index(self, index: int, add_to_history: bool = True):
        """
        Navega a una página por su índice

        Args:
            index: Índice de la página
            add_to_history: Si agregar al historial
        """
        current_index = self.stacked_widget.currentIndex()

        if add_to_history and current_index != index:
            self.history.append(current_index)

        self.stacked_widget.setCurrentIndex(index)

    def go_back(self):
        """Navega a la página anterior en el historial"""
        if self.history:
            previous_index = self.history.pop()
            self.stacked_widget.setCurrentIndex(previous_index)

    def can_go_back(self) -> bool:
        """Verifica si puede navegar hacia atrás"""
        return len(self.history) > 0

    def clear_history(self):
        """Limpia el historial de navegación"""
        self.history.clear()

    def get_current_page(self) -> Optional[QWidget]:
        """Obtiene el widget de la página actual"""
        return self.stacked_widget.currentWidget()

    def get_current_page_name(self) -> Optional[str]:
        """Obtiene el nombre de la página actual"""
        current_index = self.stacked_widget.currentIndex()
        for name, index in self.pages.items():
            if index == current_index:
                return name
        return None

    def remove_page(self, page_name: str):
        """
        Remueve una página del stack

        Args:
            page_name: Nombre de la página a remover
        """
        if page_name in self.pages:
            index = self.pages[page_name]
            widget = self.stacked_widget.widget(index)
            self.stacked_widget.removeWidget(widget)
            del self.pages[page_name]

            # Actualizar índices
            self.pages = {
                name: self.stacked_widget.indexOf(self.stacked_widget.widget(idx))
                for name, idx in self.pages.items()
            }
