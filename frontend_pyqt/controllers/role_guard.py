"""
Role Guard - Control de acceso basado en roles (RBAC)
Habilita/deshabilita elementos de UI según el rol del usuario
"""
from typing import List, Optional
from PyQt6.QtWidgets import QWidget, QPushButton, QMenu
from PyQt6.QtGui import QAction
from controllers.user_state import UserState
from resources.constants import Roles


class Permission:
    """Definición de permisos del sistema"""

    # Usuarios
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    APPROVE_USER = "approve_user"

    # Pacientes
    VIEW_PACIENTES = "view_pacientes"
    CREATE_PACIENTE = "create_paciente"
    EDIT_PACIENTE = "edit_paciente"
    DELETE_PACIENTE = "delete_paciente"

    # Boxes
    VIEW_BOXES = "view_boxes"
    CREATE_BOX = "create_box"
    EDIT_BOX = "edit_box"
    DELETE_BOX = "delete_box"

    # Atenciones
    VIEW_ATENCIONES = "view_atenciones"
    CREATE_ATENCION = "create_atencion"
    EDIT_ATENCION = "edit_atencion"
    DELETE_ATENCION = "delete_atencion"
    VIEW_OWN_ATENCIONES = "view_own_atenciones"
    EDIT_OWN_ATENCION = "edit_own_atencion"

    # Reportes
    VIEW_REPORTES = "view_reportes"
    VIEW_REPORTES_GENERALES = "view_reportes_generales"


# Matriz de permisos por rol
ROLE_PERMISSIONS = {
    Roles.ADMIN: [
        # Usuarios
        Permission.VIEW_USERS,
        Permission.CREATE_USER,
        Permission.EDIT_USER,
        Permission.DELETE_USER,
        Permission.APPROVE_USER,
        # Pacientes
        Permission.VIEW_PACIENTES,
        Permission.CREATE_PACIENTE,
        Permission.EDIT_PACIENTE,
        Permission.DELETE_PACIENTE,
        # Boxes
        Permission.VIEW_BOXES,
        Permission.CREATE_BOX,
        Permission.EDIT_BOX,
        Permission.DELETE_BOX,
        # Atenciones
        Permission.VIEW_ATENCIONES,
        Permission.CREATE_ATENCION,
        Permission.EDIT_ATENCION,
        Permission.DELETE_ATENCION,
        # Reportes
        Permission.VIEW_REPORTES,
        Permission.VIEW_REPORTES_GENERALES,
    ],
    Roles.PROFESIONAL: [
        # Pacientes
        Permission.VIEW_PACIENTES,
        Permission.CREATE_PACIENTE,
        Permission.EDIT_PACIENTE,
        # Boxes (solo lectura)
        Permission.VIEW_BOXES,
        # Atenciones (propias)
        Permission.VIEW_OWN_ATENCIONES,
        Permission.CREATE_ATENCION,
        Permission.EDIT_OWN_ATENCION,
        # Reportes (propios)
        Permission.VIEW_REPORTES,
    ],
    Roles.ADMINISTRATIVO: [
        # Pacientes (solo lectura)
        Permission.VIEW_PACIENTES,
        # Boxes (solo lectura)
        Permission.VIEW_BOXES,
        # Atenciones (solo lectura)
        Permission.VIEW_ATENCIONES,
        # Reportes (solo lectura)
        Permission.VIEW_REPORTES,
    ],
}


class RoleGuard:
    """
    Clase para controlar el acceso a elementos de UI basándose en roles
    """

    def __init__(self):
        self.user_state = UserState()

    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico

        Args:
            permission: Nombre del permiso a verificar

        Returns:
            True si tiene el permiso, False en caso contrario
        """
        if not self.user_state.is_authenticated():
            return False

        role = self.user_state.role
        if not role:
            return False

        role_perms = ROLE_PERMISSIONS.get(role, [])
        return permission in role_perms

    def has_any_permission(self, permissions: List[str]) -> bool:
        """
        Verifica si el usuario tiene al menos uno de los permisos

        Args:
            permissions: Lista de permisos

        Returns:
            True si tiene al menos uno, False en caso contrario
        """
        return any(self.has_permission(perm) for perm in permissions)

    def has_all_permissions(self, permissions: List[str]) -> bool:
        """
        Verifica si el usuario tiene todos los permisos

        Args:
            permissions: Lista de permisos

        Returns:
            True si tiene todos, False en caso contrario
        """
        return all(self.has_permission(perm) for perm in permissions)

    def guard_widget(self, widget: QWidget, permission: str, hide: bool = False):
        """
        Protege un widget basándose en un permiso

        Args:
            widget: Widget a proteger
            permission: Permiso requerido
            hide: Si True, oculta el widget. Si False, solo lo deshabilita
        """
        has_perm = self.has_permission(permission)

        if hide:
            widget.setVisible(has_perm)
        else:
            widget.setEnabled(has_perm)

    def guard_action(self, action: QAction, permission: str, hide: bool = False):
        """
        Protege una acción de menú basándose en un permiso

        Args:
            action: Acción a proteger
            permission: Permiso requerido
            hide: Si True, oculta la acción. Si False, solo la deshabilita
        """
        has_perm = self.has_permission(permission)

        if hide:
            action.setVisible(has_perm)
        else:
            action.setEnabled(has_perm)

    def guard_button(self, button: QPushButton, permission: str, hide: bool = False):
        """
        Protege un botón basándose en un permiso

        Args:
            button: Botón a proteger
            permission: Permiso requerido
            hide: Si True, oculta el botón. Si False, solo lo deshabilita
        """
        self.guard_widget(button, permission, hide)

    def require_role(self, required_role: str) -> bool:
        """
        Verifica si el usuario tiene un rol específico

        Args:
            required_role: Rol requerido

        Returns:
            True si tiene el rol, False en caso contrario
        """
        return self.user_state.has_role(required_role)

    def require_any_role(self, roles: List[str]) -> bool:
        """
        Verifica si el usuario tiene alguno de los roles especificados

        Args:
            roles: Lista de roles permitidos

        Returns:
            True si tiene alguno de los roles, False en caso contrario
        """
        return any(self.require_role(role) for role in roles)

    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.user_state.is_admin()

    def is_profesional(self) -> bool:
        """Verifica si el usuario es profesional"""
        return self.user_state.is_profesional()

    def is_administrativo(self) -> bool:
        """Verifica si el usuario es administrativo"""
        return self.user_state.is_administrativo()

    def get_allowed_sections(self) -> List[str]:
        """
        Obtiene las secciones del dashboard a las que el usuario tiene acceso

        Returns:
            Lista de nombres de secciones permitidas
        """
        sections = []

        # Secciones comunes a todos
        if self.user_state.is_authenticated():
            sections.append("Inicio")
            sections.append("Perfil")

        # Usuarios (solo admin)
        if self.has_permission(Permission.VIEW_USERS):
            sections.append("Usuarios")

        # Pacientes
        if self.has_permission(Permission.VIEW_PACIENTES):
            sections.append("Pacientes")

        # Boxes
        if self.has_permission(Permission.VIEW_BOXES):
            sections.append("Boxes")

        # Atenciones
        if self.has_any_permission([Permission.VIEW_ATENCIONES, Permission.VIEW_OWN_ATENCIONES]):
            sections.append("Atenciones")

        # Reportes
        if self.has_permission(Permission.VIEW_REPORTES):
            sections.append("Reportes")

        return sections
