import os
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

_client = None

def get_mongo_client():
    """
    Retorna la instancia singleton del cliente MongoDB.
    Si las credenciales no están configuradas, retorna None.
    """
    global _client
    mongo_uri = getattr(settings, 'MONGODB_URI', os.getenv('MONGODB_URI', ''))
    
    if not mongo_uri or not mongo_uri.strip():
        return None

    if _client is None:
        try:
            # serverSelectionTimeoutMS para que no se quede colgado si no hay internet o credenciales inválidas
            _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        except (ConfigurationError, Exception) as e:
            print(f"[mongodb] error al inicializar cliente: {e}")
            return None

    return _client

def get_mongo_db():
    """
    Retorna el objeto de la base de datos de MongoDB Atlas.
    """
    client = get_mongo_client()
    if client is None:
        return None
    db_name = getattr(settings, 'MONGODB_DB_NAME', os.getenv('MONGODB_DB_NAME', 'paraiso_cafe_nosql'))
    return client[db_name]

def check_mongo_connection():
    """
    Comprueba activamente la conexión con MongoDB Atlas ejecutando un ping.
    Retorna un diccionario con el estado y detalles.
    """
    client = get_mongo_client()
    if client is None:
        return {
            "connected": False,
            "status": "not_configured",
            "message": "MONGODB_URI no esta definido en el archivo .env"
        }

    try:
        # El comando 'ping' verifica la autenticación y conectividad con el clúster
        client.admin.command('ping')
        db_name = getattr(settings, 'MONGODB_DB_NAME', 'paraiso_cafe_nosql')
        return {
            "connected": True,
            "status": "connected",
            "database": db_name,
            "message": "conexion exitosa con mongodb atlas"
        }
    except ConnectionFailure as e:
        return {
            "connected": False,
            "status": "connection_failed",
            "message": f"fallo al conectar con el cluster atlas: {str(e)}"
        }
    except Exception as e:
        return {
            "connected": False,
            "status": "error",
            "message": f"error inesperado en mongodb: {str(e)}"
        }
