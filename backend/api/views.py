from django.db import connection
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from config.mongodb import check_mongo_connection
from .permissions import EsAdministrador, EsCliente
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


@api_view(['GET'])
def test_endpoint(request):
    """Endpoint de prueba para validar la conexión con frontend."""
    
    data = {
        "status": "success",
        "message": "conexion exitosa con el backend",
        "version": "1.0",
        "cafeteria": "paraiso del cafe"
    }
    return Response(data)


@api_view(['GET'])
def db_status_endpoint(request):
    """Endpoint de verificación de estado de las bases de datos (PSQL y MongoDB Atlas).Permite validar de forma inmediata que ambos entornos estén operativos."""
    
    # 1. Comprobar base de datos relacional (PostgreSQL / SQLite fallback)
    relational_status = {
        "engine": settings.DATABASES['default']['ENGINE'],
        "name": str(settings.DATABASES['default']['NAME']),
        "is_postgresql": 'postgresql' in settings.DATABASES['default']['ENGINE'],
        "connected": False,
        "message": ""
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row and row[0] == 1:
                relational_status["connected"] = True
                engine_name = "postgresql" if relational_status["is_postgresql"] else "sqlite (local fallback)"
                relational_status["message"] = f"conexion exitosa a {engine_name}"
    except Exception as e:
        relational_status["connected"] = False
        relational_status["message"] = f"error al conectar con base de datos relacional: {str(e)}"

    # 2. Comprobar base de datos no relacional (MongoDB Atlas)
    mongo_status = check_mongo_connection()

    # 3. Resumen global
    all_ok = relational_status["connected"] and mongo_status.get("connected", False)

    return Response({
        "status": "ok" if all_ok else "partial_or_pending",
        "timestamp": settings.TIME_ZONE,
        "bases_de_datos": {
            "relacional_psql": relational_status,
            "no_relacional_mongodb": mongo_status
        },
        "indicaciones": {
            "para_activar_psql": "configurar USE_POSTGRESQL=True en .env con las credenciales de tu servidor postgresql.",
            "para_activar_mongodb": "configurar MONGODB_URI en .env con tu string de conexion de mongodb atlas."
        }
    })

# ENDPOINT DE GESTION DE USUARIOS (LISTAR Y CREAR)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, EsAdministrador])
def list_users(request):
    """Endpoint para listar usuarios (GET) o crear un usuario individualmente (POST). Solo administradores."""
    # 1. LISTAR USUARIOS (GET)
    if request.method == 'GET':
        users = User.objects.all().order_by('id')
        users_data = []
        
        for user in users:
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "es_admin": user.is_staff
            })
            
        return Response({
            "status": "success",
            "total": len(users_data),
            "data": users_data
        }, status=status.HTTP_200_OK)

    # 2. CREACIÓN INDIVIDUAL DE USUARIOS (POST)
    elif request.method == 'POST':
        data = request.data
        email_crudo = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', data.get('nombre', ''))
        last_name = data.get('last_name', data.get('apellido', ''))
        es_admin = bool(data.get('es_admin', data.get('is_staff', False)))

        email = email_crudo.strip().lower() if email_crudo else ''

        # A. Validar campos obligatorios
        if not email or not password:
            return Response(
                {"status": "error", "message": "Faltan datos obligatorios (correo y contraseña)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # B. Validar formato de email
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"status": "error", "message": "El correo electrónico no tiene un formato válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # C. Evitar registros duplicados
        if User.objects.filter(username=email).exists():
            return Response(
                {"status": "error", "message": "Este correo ya se encuentra registrado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # D. Validar robustez de la contraseña
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {"status": "error", "message": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # E. Crear el usuario en la base de datos
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=es_admin,
            is_active=True
        )

        return Response({
            "status": "success",
            "message": "Usuario creado exitosamente.",
            "usuario": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "es_admin": user.is_staff
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, EsAdministrador])
def update_user(request, user_id):
    """Endpoint para consultar un usuario individualmente (GET) o modificar sus datos/bloquearlo (PATCH). Solo administradores."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "status": "error", 
                "message": "Usuario no encontrado"
            }, 
            status=status.HTTP_404_NOT_FOUND
        )

    # 1. CONSULTA INDIVIDUAL DE USUARIO (GET)
    if request.method == 'GET':
        return Response({
            "status": "success",
            "usuario": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "es_admin": user.is_staff,
                "fecha_registro": user.date_joined.strftime("%Y-%m-%d %H:%M") if user.date_joined else None
            }
        }, status=status.HTTP_200_OK)

    # 2. MODIFICACIÓN Y BLOQUEO DE USUARIO (PATCH)
    elif request.method == 'PATCH':
        data = request.data

        # A. Validación de seguridad al bloquear cuentas (is_active = False)
        is_active_val = None
        if 'is_active' in data:
            is_active_raw = data['is_active']
            if isinstance(is_active_raw, str):
                is_active_val = is_active_raw.strip().lower() in ('true', '1', 't')
            else:
                is_active_val = bool(is_active_raw)

            if is_active_val is False:
                # Regla 1: Prevenir auto-bloqueo del administrador en sesión
                if request.user.id == user.id:
                    return Response(
                        {
                            "status": "error",
                            "message": "No puedes suspender tu propia cuenta de administrador."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Regla 2: Prevenir bloqueo de superusuario
                if user.is_superuser:
                    return Response(
                        {
                            "status": "error",
                            "message": "No se puede suspender a un superusuario del sistema."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Regla 3: Prevenir bloqueo del último administrador activo
                if user.is_staff:
                    admins_activos = User.objects.filter(is_staff=True, is_active=True).count()
                    if admins_activos <= 1:
                        return Response(
                            {
                                "status": "error",
                                "message": "No se puede suspender al último administrador activo del sistema."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

        # B. Validación de correo único y formato si se solicita cambiar el email
        if 'email' in data:
            nuevo_email = str(data['email']).strip().lower()
            try:
                validate_email(nuevo_email)
            except ValidationError:
                return Response(
                    {
                        "status": "error",
                        "message": "El formato del correo electrónico no es válido."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que no pertenezca a otra persona
            if User.objects.filter(username=nuevo_email).exclude(id=user.id).exists():
                return Response(
                    {
                        "status": "error",
                        "message": "El correo ya está registrado por otro usuario."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = nuevo_email
            user.username = nuevo_email

        # C. Actualizar campos de texto o estado si vienen en la petición
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if is_active_val is not None:
            user.is_active = is_active_val
            
        user.save()
        
        return Response({
            "status": "success",
            "message": f"Usuario con ID {user_id} actualizado correctamente",
            "usuario": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "es_admin": user.is_staff
            }
        }, status=status.HTTP_200_OK)

#ENDPOIN DE AUTORIZACION POR ROLES
@api_view(['GET'])
@permission_classes([IsAuthenticated, EsCliente])
def perfil_cliente(request):
    """
    Endpoint protegido para clientes: muestra la información de su perfil.
    """
    return Response({
        "mensaje": f"Bienvenido a tu perfil, {request.user.first_name}.",
        "email": request.user.email,
        "rol": "Cliente"
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated, EsAdministrador])
def panel_administrador(request):
    """
    Endpoint exclusivo para administradores: gestión de la cafetería.
    """
    return Response({
        "mensaje": "Bienvenido al panel de control de la cafetería.",
        "admin": request.user.email,
        "rol": "Administrador"
    })
