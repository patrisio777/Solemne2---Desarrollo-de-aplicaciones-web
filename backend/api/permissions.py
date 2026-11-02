from rest_framework.permissions import BasePermission

class EsAdministrador(BasePermission):
    #Permiso personalizado que permite el acceso exclusivamente a usuarios con rol de administrador (is_staff = True).
    message = "Acceso denegado: Se requieren persmisos de administrador."

    def has_permission(self, request, view):
        #verificar que el usuario tiene la sesion iniciada
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )

class EsCliente(BasePermission):
    #Permite el acceso a clientes comunes (NO administradores)

    message = "Acceso denegado: Esta acción es solo para clientes."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            not request.user.is_staff
        )
