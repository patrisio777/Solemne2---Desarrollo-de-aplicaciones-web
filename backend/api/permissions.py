from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    #Permiso personalizado que permite el acceso exclusivo a usuarios con rol de administrador (is_staff = True).
    message = "Acceso denegado: Se requieren permisos de administrador."

    def has_permission(self, request, view):
        #Verificar que el usuario tiene la sesion iniciada, esta activo y es administrador
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            (request.user.is_staff or request.user.is_superuser)
        )


class EsCliente(BasePermission):
    #Permite el acceso a clientes comunes (NO administradores)
    message = "Acceso denegado: Esta accion es solo para clientes."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active and
            not request.user.is_staff
        )
