from django.db import connection
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from config.mongodb import check_mongo_connection
#importancion del modelo de usuario
from django.contrib.auth.models import User
from rest_framework import status

@api_view(['GET'])
def test_endpoint(request):
    """
    Endpoint de prueba para validar la conexión con frontend.
    """
    data = {
        "status": "success",
        "message": "conexion exitosa con el backend",
        "version": "1.0",
        "cafeteria": "paraiso del cafe"
    }
    return Response(data)


@api_view(['GET'])
def db_status_endpoint(request):
    """
    Endpoint de verificación de estado de las bases de datos (PSQL y MongoDB Atlas).
    Permite validar de forma inmediata que ambos entornos estén operativos.
    """
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
@api_view(['GET'])
def list_users(request):
    """
    Endpoint para listar todos los usuarios del sistema.
    """
    users = User.objects.all()
    users_data = []
    
    for user in users:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
        
    return Response({
        "status": "success",
        "message": "Usuarios obtenidos correctamente",
        "data": users_data
    })

@api_view(['PATCH'])
def update_user(request, user_id):
    """
    Endpoint para actualizar datos de un usuario o cambiar su estado (activo/inactivo).
    """
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
    
    # Obtenemos los datos que envía el Frontend en el JSON
    data = request.data
    
    # Actualizamos solo los campos que vengan en la petición
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'is_active' in data:
        user.is_active = data['is_active']
        
    user.save() # Guardamos los cambios en la base de datos
    
    return Response({
        "status": "success",
        "message": f"Usuario con ID {user_id} actualizado correctamente"
    })

