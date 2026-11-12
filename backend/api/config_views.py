"""
ENDPOINTS SPRINT 4: TEMA VISUAL ACTIVO Y MENSAJES DE CONTACTO (PostgreSQL).

Rutas:
- GET   /api/tema/                 tema activo (público; HU-06 / RF-04)
- POST  /api/tema/                 guardar tema activo (solo administradores)
- POST  /api/contacto/             recibir mensaje del formulario (público; HU-07 / RF-05)
- GET   /api/contacto/mensajes/    consultar mensajes recibidos (solo administradores)

Reglas cubiertas:
- Guardar tema en PostgreSQL, validando que sea uno de los cuatro aprobados
  (claro, oscuro, vintage, pastel) y rechazando identificadores inexistentes.
- El tema persiste tras reiniciar el servidor.
- Mensajes: nombre de 2 a 100 caracteres, correo con formato válido y mensaje
  de 10 a 2.000 caracteres, con error por campo; nunca se informa éxito si el
  almacenamiento falla.
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MensajeContacto, TemaVisual
from .permissions import EsAdministrador

# Límites del formulario de contacto (HU-07 / RF-05)
NOMBRE_MIN, NOMBRE_MAX = 2, 100
MENSAJE_MIN, MENSAJE_MAX = 10, 2000


def _es_admin(user):
    return bool(user and user.is_authenticated and user.is_active
                and (user.is_staff or user.is_superuser))


def _serializar_tema(tema):
    return {
        "identificador": tema.pk,
        "nombre": tema.nombre,
        "etiqueta": tema.etiqueta,
        "actualizado_en": tema.actualizado_en.isoformat() if tema.actualizado_en else None,
    }


# ==============================================================================
# 1. TEMA VISUAL ACTIVO (HU-06 / RF-04)
# ==============================================================================
@api_view(['GET', 'POST'])
def tema_activo(request):
    """GET: devuelve el tema activo persistido en PostgreSQL.
    POST (solo administradores): guarda el tema activo validando que sea uno
    de los cuatro aprobados; acepta `identificador` (pk) o `nombre`."""
    if request.method == 'GET':
        tema = TemaVisual.garantizar_temas()
        return Response(
            {"status": "success", "tema": _serializar_tema(tema)},
            status=status.HTTP_200_OK,
        )

    if not _es_admin(request.user):
        # DRF traduce esto a 401 anónimo / 403 sin rol de administrador
        from rest_framework.exceptions import PermissionDenied, NotAuthenticated
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied("Solo los administradores pueden cambiar el tema activo.")

    TemaVisual.garantizar_temas()
    identificador = request.data.get('identificador')
    nombre = request.data.get('nombre', request.data.get('tema'))

    tema = None
    if identificador is not None:
        try:
            tema = TemaVisual.objects.get(pk=identificador)
        except (TemaVisual.DoesNotExist, ValueError, TypeError):
            return Response(
                {"status": "error", "message": "El identificador del tema no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )
    elif nombre is not None:
        if not isinstance(nombre, str) or nombre.strip().lower() not in TemaVisual.NOMBRES_APROBADOS:
            return Response(
                {"status": "error",
                 "message": "El tema debe ser uno de: claro, oscuro, vintage, pastel."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tema = TemaVisual.objects.get(nombre=nombre.strip().lower())
    else:
        return Response(
            {"status": "error", "errores": {"nombre": ["Falta el tema a activar (nombre o identificador)."]}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Un solo tema activo a la vez
    TemaVisual.objects.filter(activo=True).update(activo=False)
    tema.activo = True
    tema.save(update_fields=['activo', 'actualizado_en'])

    return Response(
        {"status": "success", "message": "Tema activo actualizado.", "tema": _serializar_tema(tema)},
        status=status.HTTP_200_OK,
    )


# ==============================================================================
# 2. MENSAJES DE CONTACTO (HU-07 / RF-05)
# ==============================================================================
def _validar_mensaje(data):
    errores = {}

    nombre = data.get('nombre')
    if not isinstance(nombre, str) or not (NOMBRE_MIN <= len(nombre.strip()) <= NOMBRE_MAX):
        errores['nombre'] = [f"El nombre debe tener entre {NOMBRE_MIN} y {NOMBRE_MAX} caracteres."]

    email = data.get('email')
    if not isinstance(email, str) or not email.strip():
        errores['email'] = ["El correo es obligatorio."]
    else:
        try:
            validate_email(email.strip())
        except ValidationError:
            errores['email'] = ["El correo no tiene un formato valido."]

    mensaje = data.get('mensaje')
    if not isinstance(mensaje, str) or not (MENSAJE_MIN <= len(mensaje.strip()) <= MENSAJE_MAX):
        errores['mensaje'] = [f"El mensaje debe tener entre {MENSAJE_MIN} y {MENSAJE_MAX} caracteres."]

    return errores


@api_view(['POST'])
def crear_mensaje_contacto(request):
    """Recibe y almacena un mensaje del formulario de contacto (público)."""
    errores = _validar_mensaje(request.data)
    if errores:
        return Response(
            {"status": "error", "errores": errores},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        MensajeContacto.objects.create(
            nombre=request.data['nombre'].strip(),
            email=request.data['email'].strip(),
            mensaje=request.data['mensaje'].strip(),
        )
    except Exception:
        # Nunca informar éxito si el almacenamiento falló
        return Response(
            {"status": "error",
             "message": "No fue posible almacenar el mensaje. Intenta nuevamente."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {"status": "success", "message": "Mensaje almacenado correctamente."},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, EsAdministrador])
def listar_mensajes_contacto(request):
    """Consulta de los mensajes de contacto recibidos (solo administradores)."""
    mensajes = MensajeContacto.objects.all()[:100]
    return Response({
        "status": "success",
        "total": MensajeContacto.objects.count(),
        "mensajes": [
            {
                "id": m.pk,
                "nombre": m.nombre,
                "email": m.email,
                "mensaje": m.mensaje,
                "leido": m.leido,
                "creado_en": m.creado_en.isoformat() if m.creado_en else None,
            }
            for m in mensajes
        ],
    }, status=status.HTTP_200_OK)
