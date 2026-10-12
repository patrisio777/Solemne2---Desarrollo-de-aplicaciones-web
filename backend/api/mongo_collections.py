"""
TAREA 2 BACKEND: MODELOS Y COLECCIONES NO RELACIONALES (MongoDB Atlas)

Justificación:
MongoDB Atlas almacena información semiestructurada, altamente variable y de alto volumen
que no requiere integridad referencial rígida ACID ni bloqueos de transacciones financieras.
Ideal para:
  1. Logs crudos de pasarela de pago (auditoría forense de webhooks de terceros).
  2. Formularios dinámicos de contacto.
  3. Fichas sensoriales de cafés (notas de cata, procesos, atributos variables).
  4. Reseñas y valoraciones de usuarios.
"""

from datetime import datetime
from config.mongodb import get_mongo_db

# Nombres estándar de las colecciones en MongoDB Atlas
COLLECTION_LOGS_PAGOS = "logs_pasarela_pagos"
COLLECTION_CONTACTO = "mensajes_contacto"
COLLECTION_FICHAS_CAFE = "fichas_tecnicas_cafe"
COLLECTION_RESENAS = "resenas_productos"


# ==============================================================================
# 1. LOGS DE AUDITORÍA Y WEBHOOKS DE LA PASARELA DE PAGOS
# ==============================================================================
def registrar_log_pasarela(pedido_id, accion, pasarela, payload_crudo, status_code=200, ip_origen=None):
    """
    Registra el evento y payload JSON en bruto recibido desde la pasarela externa
    (Transbank Webpay, Stripe o Mercado Pago).
    
    Estructura del Documento en MongoDB:
    {
        "_id": ObjectId(...),
        "pedido_id": 104,
        "pasarela": "Webpay Plus",
        "accion": "CONFIRMAR_TRANSACCION",
        "timestamp": ISODate("2026-10-10T21:40:00Z"),
        "payload_crudo": { ...JSON recibido sin filtrar... },
        "status_code": 200,
        "ip_origen": "190.160.0.1",
        "exito": True
    }
    """
    db = get_mongo_db()
    if db is None:
        print("[mongodb] no disponible para registrar log de pasarela.")
        return None

    documento = {
        "pedido_id": pedido_id,
        "pasarela": pasarela,
        "accion": accion,
        "timestamp": datetime.utcnow(),
        "payload_crudo": payload_crudo,
        "status_code": status_code,
        "ip_origen": ip_origen,
        "exito": 200 <= status_code < 300
    }
    resultado = db[COLLECTION_LOGS_PAGOS].insert_one(documento)
    return str(resultado.inserted_id)


# ==============================================================================
# 2. MENSAJES DEL FORMULARIO DE CONTACTO (/contacto)
# ==============================================================================
def guardar_mensaje_contacto(nombre, email, asunto, mensaje, datos_extra=None):
    """
    Almacena las consultas del formulario de contacto.
    Permite campos personalizados (datos_extra) según la consulta.
    
    Estructura del Documento en MongoDB:
    {
        "_id": ObjectId(...),
        "nombre": "Francisca Silva",
        "email": "francisca@ejemplo.cl",
        "asunto": "Consulta eventos corporativos",
        "mensaje": "Quisiera cotizar una barra móvil para...",
        "datos_extra": { "telefono": "+569...", "ciudad": "Santiago" },
        "leido": False,
        "respondido": False,
        "creado_en": ISODate(...)
    }
    """
    db = get_mongo_db()
    if db is None:
        return None

    documento = {
        "nombre": nombre,
        "email": email,
        "asunto": asunto,
        "mensaje": mensaje,
        "datos_extra": datos_extra or {},
        "leido": False,
        "respondido": False,
        "creado_en": datetime.utcnow()
    }
    resultado = db[COLLECTION_CONTACTO].insert_one(documento)
    return str(resultado.inserted_id)


# ==============================================================================
# 3. FICHAS TÉCNICAS Y NOTAS SENSORIALES DE CAFÉS DE ESPECIALIDAD
# ==============================================================================
def guardar_ficha_tecnica_cafe(producto_id, ficha_data):
    """
    Guarda o actualiza las propiedades sensoriales y de origen de un café.
    
    Estructura del Documento en MongoDB:
    {
        "producto_id": 12,
        "origen": {
            "pais": "Etiopía",
            "region": "Yirgacheffe",
            "finca": "Idido",
            "altitud_msnm": 2100
        },
        "variedad_botanica": ["Heirloom", "Kurume"],
        "proceso": "Lavado",
        "perfil_tueste": "Medio-Claro",
        "notas_de_cata": ["Jazmín", "Bergamota", "Miel de azahar"],
        "acidez": 4.5,
        "cuerpo": 3.0,
        "dulzor": 4.8,
        "recomendacion_extraccion": ["V60", "Aeropress", "Chemex"]
    }
    """
    db = get_mongo_db()
    if db is None:
        return None

    ficha_data["producto_id"] = producto_id
    ficha_data["actualizado_en"] = datetime.utcnow()
    resultado = db[COLLECTION_FICHAS_CAFE].update_one(
        {"producto_id": producto_id},
        {"$set": ficha_data},
        upsert=True
    )
    return resultado.acknowledged


# ==============================================================================
# 4. RESEÑAS Y VALORACIONES DE USUARIOS
# ==============================================================================
def guardar_resena_producto(producto_id, usuario_nombre, rating, comentario, tags=None):
    """
    Guarda opiniones de productos con ratings variables y tags.
    """
    db = get_mongo_db()
    if db is None:
        return None

    documento = {
        "producto_id": producto_id,
        "usuario_nombre": usuario_nombre,
        "rating": rating,
        "comentario": comentario,
        "tags": tags or [],
        "aprobado": True,
        "creado_en": datetime.utcnow()
    }
    resultado = db[COLLECTION_RESENAS].insert_one(documento)
    return str(resultado.inserted_id)
