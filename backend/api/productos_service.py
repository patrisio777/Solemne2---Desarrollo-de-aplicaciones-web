"""
TAREA SPRINT 3/4 BACKEND: PRODUCTOS EN MONGODB ATLAS (HU-08 / HU-09 / RF-16..RF-21)

Justificación (spec): "MongoDB Atlas: productos, registro de inicios de sesión,
registro de ajustes de stock". Catálogo semiestructurado con galería de imágenes
variable (4 a 6), sin claves foráneas, de alta lectura para el catálogo público.

Esquema del documento producto:
{
    "identificador": "capuccino-de-especialidad-a1b2c3",   # inmutable
    "nombre": "Capuccino de Especialidad",
    "descripcion": "...",
    "precio": 4500,                  # entero o decimal > 0
    "moneda": "CLP",
    "stock_fisico": 25,
    "stock_reservado": 3,            # <= stock_fisico
    "estado": "activo" | "inactivo", # inactivo = desactivado (nunca se borra)
    "imagenes": ["https://...", ...],# entre 4 y 6
    "creado_en": ISODate(...),
    "actualizado_en": ISODate(...)
}

Reglas de negocio cubiertas:
- RNF-03: máximo 50 productos por respuesta (paginación con skip/limit en Mongo).
- Creación: nombre y descripción no vacíos, precio > 0, stock entero >= 0,
  entre 4 y 6 imágenes.
- Consulta de catálogo: solo activos; stock cero = agotado (disponible=False).
- Ajuste de stock: entero >= 0 y nunca menor al stock reservado; cada ajuste
  deja registro de auditoría (producto, valor anterior, valor nuevo,
  administrador, fecha) en la colección `ajustes_stock`.
- Edición: el identificador es inmutable; el stock se ajusta solo por su
  endpoint dedicado; la desactivación no elimina el documento.
"""

import random
import re
import unicodedata
from datetime import datetime

from config.mongodb import get_mongo_db

# Colecciones en MongoDB Atlas
COLLECTION_PRODUCTOS = "productos"
COLLECTION_AJUSTES_STOCK = "ajustes_stock"

# RNF-03: máximo de productos por respuesta
MAX_POR_PAGINA = 50
MIN_POR_PAGINA = 1
TAMANO_DEFECTO = 12

ESTADOS_VALIDOS = ("activo", "inactivo")
CAMPOS_EDITABLES = {"nombre", "descripcion", "precio", "moneda", "imagenes"}


class ErrorValidacion(Exception):
    """Errores de validación por campo; se traducen a HTTP 400."""

    def __init__(self, errores):
        self.errores = errores
        super().__init__(str(errores))


class BaseDatosNoDisponible(Exception):
    """MongoDB Atlas sin configurar o inalcanzable; se traduce a HTTP 503."""


def _conexion(db=None):
    base = db if db is not None else get_mongo_db()
    if base is None:
        raise BaseDatosNoDisponible(
            "MongoDB Atlas no esta disponible (revisar MONGODB_URI en .env)."
        )
    return base


def _documento_publico(doc):
    """Serializa un documento para la API (sin _id interno de Mongo)."""
    if doc is None:
        return None
    copia = {k: v for k, v in doc.items() if k != "_id"}
    stock_fisico = copia.get("stock_fisico", 0)
    imagenes = copia.get("imagenes") or []
    copia["imagen_principal"] = imagenes[0] if imagenes else None
    copia["disponible"] = stock_fisico > 0 and copia.get("estado") == "activo"
    copia["agotado"] = stock_fisico <= 0
    return copia


def _validar_texto(valor, campo, errores, minimo=1, maximo=500):
    if not isinstance(valor, str) or not valor.strip():
        errores[campo] = [f"El campo '{campo}' es obligatorio y no puede estar vacio."]
        return None
    texto = valor.strip()
    if len(texto) < minimo:
        errores[campo] = [f"El campo '{campo}' debe tener al menos {minimo} caracteres."]
        return None
    if len(texto) > maximo:
        errores[campo] = [f"El campo '{campo}' no puede superar {maximo} caracteres."]
        return None
    return texto


def _validar_numero(valor, campo, errores, minimo=None, entero=False):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
        errores[campo] = [f"El campo '{campo}' debe ser un numero."]
        return None
    try:
        numero = int(valor) if entero else float(valor)
    except (TypeError, ValueError):
        errores[campo] = [f"El campo '{campo}' debe ser un numero."]
        return None
    if entero and float(valor) != float(numero):
        errores[campo] = [f"El campo '{campo}' debe ser un numero entero."]
        return None
    if minimo is not None and numero < minimo:
        errores[campo] = [f"El campo '{campo}' debe ser mayor o igual a {minimo}."]
        return None
    return numero


def _validarimagenes(valor, errores, requerido=False):
    if valor is None and not requerido:
        return None
    if not isinstance(valor, list):
        errores["imagenes"] = ["El campo 'imagenes' debe ser una lista de 4 a 6 URLs."]
        return None
    if not 4 <= len(valor) <= 6:
        errores["imagenes"] = ["La galeria debe tener entre 4 y 6 imagenes."]
        return None
    limpias = []
    for indice, url in enumerate(valor):
        if not isinstance(url, str) or not url.strip():
            errores["imagenes"] = [f"La imagen {indice + 1} no es una URL valida."]
            return None
        limpias.append(url.strip())
    return limpias


def validar_producto(data, completo=True):
    """
    Valida los datos de un producto. Con completo=True exige todos los campos
    de creación; con completo=False valida solo los campos presentes (edición).
    Devuelve los datos normalizados o lanza ErrorValidacion con errores por campo.
    """
    errores = {}
    normalizado = {}

    if completo or "nombre" in data:
        nombre = _validar_texto(data.get("nombre"), "nombre", errores, minimo=2, maximo=150)
        if nombre:
            normalizado["nombre"] = nombre

    if completo or "descripcion" in data:
        descripcion = _validar_texto(data.get("descripcion"), "descripcion", errores, minimo=10, maximo=5000)
        if descripcion:
            normalizado["descripcion"] = descripcion

    if completo or "precio" in data:
        precio = _validar_numero(data.get("precio"), "precio", errores, minimo=0.01)
        if precio is not None:
            normalizado["precio"] = precio

    if "moneda" in data and data.get("moneda") not in (None, ""):
        moneda = data.get("moneda")
        if not isinstance(moneda, str) or not re.fullmatch(r"[A-Za-z]{3}", moneda.strip()):
            errores["moneda"] = ["La moneda debe ser un codigo de 3 letras (ej: CLP)."]
        else:
            normalizado["moneda"] = moneda.strip().upper()
    elif completo:
        normalizado["moneda"] = "CLP"

    if completo or "stock_fisico" in data:
        stock = _validar_numero(data.get("stock_fisico"), "stock_fisico", errores, minimo=0, entero=True)
        if stock is not None:
            normalizado["stock_fisico"] = stock

    if "stock_reservado" in data:
        reservado = _validar_numero(data.get("stock_reservado"), "stock_reservado", errores, minimo=0, entero=True)
        if reservado is not None:
            normalizado["stock_reservado"] = reservado

    if "estado" in data:
        estado = data.get("estado")
        if estado not in ESTADOS_VALIDOS:
            errores["estado"] = ["El estado debe ser 'activo' o 'inactivo'."]
        else:
            normalizado["estado"] = estado
    elif completo:
        normalizado["estado"] = "activo"

    imagenes = _validarimagenes(data.get("imagenes"), errores, requerido=completo)
    if imagenes is not None:
        normalizado["imagenes"] = imagenes

    if errores:
        raise ErrorValidacion(errores)

    stock_fisico = normalizado.get("stock_fisico")
    reservado = normalizado.get("stock_reservado")
    if stock_fisico is not None and reservado is not None and reservado > stock_fisico:
        raise ErrorValidacion(
            {"stock_reservado": ["El stock reservado no puede superar al stock fisico."]}
        )
    return normalizado


def _slugificar(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto or "producto"


def _generar_identificador(db, nombre):
    base = _slugificar(nombre)[:80]
    while True:
        candidato = f"{base}-{random.randint(100000, 999999)}"
        if db[COLLECTION_PRODUCTOS].find_one({"identificador": candidato}) is None:
            return candidato


def _pagina_entera(valor, campo, errores):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        errores[campo] = [f"El parametro '{campo}' debe ser un numero entero."]
        return None
    if numero < 1:
        errores[campo] = [f"El parametro '{campo}' debe ser 1 o mayor."]
        return None
    return numero


# ==============================================================================
# 1. CONSULTA DE CATÁLOGO CON PAGINACIÓN (HU-09 / RF-20 / RNF-03)
# ==============================================================================
def listar_catalogo(pagina=1, tamano=TAMANO_DEFECTO, solo_activos=True, db=None):
    """Devuelve una página de productos y la información de paginación.
    En Mongo solo se traen los documentos de la página pedida (skip/limit)."""
    base = _conexion(db)
    errores = {}
    pagina = _pagina_entera(pagina, "pagina", errores)
    tamano = _pagina_entera(tamano, "tamano", errores)
    if tamano is not None and tamano > MAX_POR_PAGINA:
        errores["tamano"] = [f"El maximo de productos por respuesta es {MAX_POR_PAGINA} (RNF-03)."]
    if errores:
        raise ErrorValidacion(errores)

    filtro = {"estado": "activo"} if solo_activos else {}
    coleccion = base[COLLECTION_PRODUCTOS]
    total = coleccion.count_documents(filtro)
    total_paginas = max(1, -(-total // tamano))  # ceil

    cursor = (
        coleccion.find(filtro)
        .sort("creado_en", -1)
        .skip((pagina - 1) * tamano)
        .limit(tamano)
    )
    productos = [_documento_publico(doc) for doc in cursor]

    return {
        "paginacion": {
            "pagina": pagina,
            "tamano": tamano,
            "total": total,
            "total_paginas": total_paginas,
            "hay_siguiente": pagina < total_paginas,
            "hay_anterior": pagina > 1 and total > 0,
        },
        "productos": productos,
    }


# ==============================================================================
# 2. CONSULTA INDIVIDUAL (HU-09)
# ==============================================================================
def obtener_producto(identificador, db=None):
    base = _conexion(db)
    return base[COLLECTION_PRODUCTOS].find_one({"identificador": identificador})


# ==============================================================================
# 3. CREACIÓN DE PRODUCTOS (HU-08 / RF-16)
# ==============================================================================
def crear_producto(data, db=None):
    base = _conexion(db)
    datos = validar_producto(data, completo=True)
    ahora = datetime.utcnow()
    documento = {
        "identificador": _generar_identificador(base, datos["nombre"]),
        "stock_reservado": 0,
        **datos,
        "creado_en": ahora,
        "actualizado_en": ahora,
    }
    base[COLLECTION_PRODUCTOS].insert_one(documento)
    return _documento_publico(documento)


# ==============================================================================
# 4. EDICIÓN (HU-08 / RF-17): identificador inmutable, stock solo por su endpoint
# ==============================================================================
def editar_producto(identificador, data, db=None):
    base = _conexion(db)
    existente = obtener_producto(identificador, base)
    if existente is None:
        return None

    if "identificador" in data and data["identificador"] != identificador:
        raise ErrorValidacion({"identificador": ["El identificador es inmutable."]})

    recibidos = set(data) - {"identificador"}
    no_permitidos = recibidos - CAMPOS_EDITABLES
    if no_permitidos:
        raise ErrorValidacion({
            campo: ["Este campo no se edita aqui; usa el endpoint de stock o de estado."]
            for campo in sorted(no_permitidos)
        })
    if not recibidos:
        raise ErrorValidacion({"general": ["No se recibieron campos para editar."]})

    datos = validar_producto(
        {k: v for k, v in data.items() if k in CAMPOS_EDITABLES}, completo=False
    )
    # Mantener coherencia precio/moneda con lo ya almacenado sin invalidar
    # ediciones que no tocan esos campos.
    base[COLLECTION_PRODUCTOS].update_one(
        {"identificador": identificador},
        {"$set": {**datos, "actualizado_en": datetime.utcnow()}},
    )
    return _documento_publico(obtener_producto(identificador, base))


# ==============================================================================
# 5. DESACTIVACIÓN SIN ELIMINAR (HU-08 / RF-18)
# ==============================================================================
def cambiar_estado(identificador, estado, db=None):
    base = _conexion(db)
    if estado not in ESTADOS_VALIDOS:
        raise ErrorValidacion({"estado": ["El estado debe ser 'activo' o 'inactivo'."]})
    existente = obtener_producto(identificador, base)
    if existente is None:
        return None
    # Nunca se elimina el documento: solo cambia su estado.
    base[COLLECTION_PRODUCTOS].update_one(
        {"identificador": identificador},
        {"$set": {"estado": estado, "actualizado_en": datetime.utcnow()}},
    )
    return _documento_publico(obtener_producto(identificador, base))


# ==============================================================================
# 6. AJUSTE DE STOCK CON AUDITORÍA (HU-08 / RF-19)
# ==============================================================================
def ajustar_stock(identificador, nuevo_valor, administrador, db=None):
    """Ajusta el stock físico validando entero >= 0 y >= stock_reservado, y
    registra la auditoría: producto, valor anterior, valor nuevo,
    administrador y fecha (colección `ajustes_stock`)."""
    base = _conexion(db)
    errores = {}
    valor = _validar_numero(nuevo_valor, "stock_fisico", errores, minimo=0, entero=True)
    if errores:
        raise ErrorValidacion(errores)

    existente = obtener_producto(identificador, base)
    if existente is None:
        return None

    reservado = existente.get("stock_reservado", 0)
    if valor < reservado:
        raise ErrorValidacion({
            "stock_fisico": [
                f"El stock fisico no puede quedar por debajo del reservado ({reservado})."
            ]
        })

    anterior = existente.get("stock_fisico", 0)
    base[COLLECTION_PRODUCTOS].update_one(
        {"identificador": identificador},
        {"$set": {"stock_fisico": valor, "actualizado_en": datetime.utcnow()}},
    )
    base[COLLECTION_AJUSTES_STOCK].insert_one({
        "producto_identificador": identificador,
        "producto_nombre": existente.get("nombre"),
        "valor_anterior": anterior,
        "valor_nuevo": valor,
        "administrador": {
            "id": getattr(administrador, "pk", None),
            "email": getattr(administrador, "email", None) or getattr(administrador, "username", None),
        },
        "fecha": datetime.utcnow(),
    })
    return _documento_publico(obtener_producto(identificador, base))
