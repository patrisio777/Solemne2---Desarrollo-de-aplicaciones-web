"""
ENDPOINTS DE PRODUCTOS (Sprint 3/4) — catálogo público y gestión de administración.

Rutas:
- GET    /api/productos/                     catálogo paginado (solo activos, RNF-03)
- GET    /api/productos/?pagina=&tamano=     parámetros de paginación
- GET    /api/productos/?todos=1             vista de gestión (solo administradores)
- POST   /api/productos/                     creación (solo administradores)
- GET    /api/productos/<identificador>/     detalle (inactivos solo para administradores)
- PUT    /api/productos/<identificador>/     edición de nombre/descripción/precio/imágenes
- PATCH  /api/productos/<identificador>/estado/   activar o desactivar sin eliminar
- PATCH  /api/productos/<identificador>/stock/    ajuste de stock con auditoría

El acceso de escritura se controla por método (GET público / POST·PUT·PATCH de
administrador) porque ambas operaciones comparten la misma ruta.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from . import productos_service
from .productos_service import (
    BaseDatosNoDisponible,
    ErrorValidacion,
)


def _respuesta_error(exc):
    """Convierte las excepciones del servicio en respuestas HTTP estándar."""
    if isinstance(exc, ErrorValidacion):
        return Response(
            {"status": "error", "errores": exc.errores},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if isinstance(exc, BaseDatosNoDisponible):
        return Response(
            {"status": "error", "message": str(exc)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(
        {"status": "error", "message": "Error inesperado al consultar los productos."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _es_admin(user):
    return bool(user and user.is_authenticated and user.is_active
                and (user.is_staff or user.is_superuser))


def _requerir_admin(request):
    """401 si no hay credenciales; 403 si no es administrador."""
    if not _es_admin(request.user):
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied("Se requieren permisos de administrador.")


def _no_encontrado():
    return Response(
        {"status": "error", "message": "Producto no encontrado."},
        status=status.HTTP_404_NOT_FOUND,
    )


# ==============================================================================
# 1. CATÁLOGO (GET) Y CREACIÓN (POST) — /api/productos/
# ==============================================================================
def _listar_productos(request):
    """Catálogo público paginado. Con ?todos=1 (solo administradores) incluye
    los productos inactivos para su gestión."""
    pagina = request.query_params.get('pagina', 1)
    tamano = request.query_params.get('tamano', productos_service.TAMANO_DEFECTO)

    incluir_inactivos = request.query_params.get('todos') in ('1', 'true', 'True')
    if incluir_inactivos and not _es_admin(request.user):
        return Response(
            {"status": "error", "message": "Se requieren permisos de administrador."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        resultado = productos_service.listar_catalogo(
            pagina=pagina, tamano=tamano, solo_activos=not incluir_inactivos
        )
    except ErrorValidacion as exc:
        return _respuesta_error(exc)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    return Response({"status": "success", **resultado}, status=status.HTTP_200_OK)


def _crear_producto(request):
    try:
        producto = productos_service.crear_producto(request.data)
    except ErrorValidacion as exc:
        return _respuesta_error(exc)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    return Response(
        {"status": "success", "message": "Producto creado correctamente.", "producto": producto},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'POST'])
def catalogo_productos(request):
    if request.method == 'POST':
        _requerir_admin(request)
        return _crear_producto(request)
    return _listar_productos(request)


# ==============================================================================
# 2. DETALLE (GET) Y EDICIÓN (PUT) — /api/productos/<identificador>/
# ==============================================================================
def _detalle_producto(request, identificador):
    """Detalle de un producto. Los inactivos solo son visibles para administradores."""
    try:
        documento = productos_service.obtener_producto(identificador)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    if documento is None:
        return _no_encontrado()

    producto = productos_service._documento_publico(documento)
    if producto["estado"] != "activo" and not _es_admin(request.user):
        return _no_encontrado()

    return Response({"status": "success", "producto": producto}, status=status.HTTP_200_OK)


def _editar_producto(request, identificador):
    """Edita nombre, descripción, precio, moneda e imágenes. El identificador
    es inmutable y el stock no se edita aquí."""
    try:
        producto = productos_service.editar_producto(identificador, request.data)
    except ErrorValidacion as exc:
        return _respuesta_error(exc)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    if producto is None:
        return _no_encontrado()
    return Response(
        {"status": "success", "message": "Producto actualizado correctamente.", "producto": producto},
        status=status.HTTP_200_OK,
    )


@api_view(['GET', 'PUT'])
def detalle_o_edicion(request, identificador):
    if request.method == 'PUT':
        _requerir_admin(request)
        return _editar_producto(request, identificador)
    return _detalle_producto(request, identificador)


# ==============================================================================
# 3. ESTADO (PATCH) — activar o desactivar sin eliminar (RF-18)
# ==============================================================================
@api_view(['PATCH'])
def cambiar_estado_producto(request, identificador):
    _requerir_admin(request)
    estado = request.data.get('estado')
    if estado is None and 'activo' in request.data:
        estado = 'activo' if request.data.get('activo') else 'inactivo'

    try:
        producto = productos_service.cambiar_estado(identificador, estado)
    except ErrorValidacion as exc:
        return _respuesta_error(exc)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    if producto is None:
        return _no_encontrado()
    return Response(
        {"status": "success", "message": f"Producto {producto['estado']}.", "producto": producto},
        status=status.HTTP_200_OK,
    )


# ==============================================================================
# 4. AJUSTE DE STOCK (PATCH) — con registro de auditoría (RF-19)
# ==============================================================================
@api_view(['PATCH'])
def ajustar_stock_producto(request, identificador):
    _requerir_admin(request)
    nuevo_valor = request.data.get('stock_fisico')
    if nuevo_valor is None:
        return Response(
            {"status": "error", "errores": {"stock_fisico": ["Falta el nuevo valor de stock fisico."]}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        producto = productos_service.ajustar_stock(
            identificador, nuevo_valor, administrador=request.user
        )
    except ErrorValidacion as exc:
        return _respuesta_error(exc)
    except BaseDatosNoDisponible as exc:
        return _respuesta_error(exc)

    if producto is None:
        return _no_encontrado()
    return Response(
        {"status": "success", "message": "Stock ajustado y registrado en la auditoria.",
         "producto": producto},
        status=status.HTTP_200_OK,
    )
