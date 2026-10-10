from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(usuario and usuario.is_authenticated and (usuario.is_staff or usuario.is_superuser))
