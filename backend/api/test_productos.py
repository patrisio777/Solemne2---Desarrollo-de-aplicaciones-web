"""
Pruebas del catálogo de productos en MongoDB Atlas (Sprint 3/4).
HU-08 / HU-09 · RF-16 a RF-21 · RNF-03 (máximo 50 productos por respuesta).

Se usa una base de datos falsa en memoria para no depender de la red.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


# ==============================================================================
# Base de datos MongoDB falsa (solo los métodos que usa el servicio)
# ==============================================================================
class _CursorFalso:
    def __init__(self, documentos):
        self._documentos = documentos
        self._orden = None
        self._salto = 0
        self._limite = None

    def sort(self, campo, direccion):
        self._orden = (campo, direccion)
        return self

    def skip(self, cantidad):
        self._salto = cantidad
        return self

    def limit(self, cantidad):
        self._limite = cantidad
        return self

    def __iter__(self):
        documentos = list(self._documentos)
        if self._orden:
            campo, direccion = self._orden
            documentos.sort(key=lambda d: d.get(campo), reverse=direccion == -1)
        if self._salto:
            documentos = documentos[self._salto:]
        if self._limite is not None:
            documentos = documentos[: self._limite]
        return iter(documentos)


class _ColeccionFalsa:
    def __init__(self):
        self.documentos = []
        self._contador = 0

    @staticmethod
    def _coincide(documento, filtro):
        return all(documento.get(k) == v for k, v in filtro.items())

    def insert_one(self, documento):
        guardado = dict(documento)
        self._contador += 1
        guardado.setdefault("_id", f"oid{self._contador}")
        self.documentos.append(guardado)
        return SimpleNamespace(inserted_id=guardado["_id"])

    def find_one(self, filtro):
        for documento in self.documentos:
            if self._coincide(documento, filtro):
                return documento
        return None

    def find(self, filtro):
        return _CursorFalso([d for d in self.documentos if self._coincide(d, filtro)])

    def count_documents(self, filtro):
        return sum(1 for d in self.documentos if self._coincide(d, filtro))

    def update_one(self, filtro, actualizacion, upsert=False):
        for documento in self.documentos:
            if self._coincide(documento, filtro):
                documento.update(actualizacion.get("$set", {}))
                return SimpleNamespace(matched_count=1, modified_count=1)
        if upsert:
            nuevo = dict(filtro)
            nuevo.update(actualizacion.get("$set", {}))
            return self.insert_one(nuevo)
        return SimpleNamespace(matched_count=0, modified_count=0)


class _BaseMongoFalsa:
    def __init__(self):
        self._colecciones = {}

    def __getitem__(self, nombre):
        return self._colecciones.setdefault(nombre, _ColeccionFalsa())


def _producto_fake(indice, **campos):
    documento = {
        "identificador": f"producto-{indice}",
        "nombre": f"Producto {indice}",
        "descripcion": "Descripcion de prueba suficientemente larga",
        "precio": 4500,
        "moneda": "CLP",
        "stock_fisico": 5,
        "stock_reservado": 0,
        "estado": "activo",
        "imagenes": [f"https://imagenes.cafe/{indice}/{n}.jpg" for n in range(4)],
        "creado_en": datetime(2026, 1, 1) + timedelta(minutes=indice),
        "actualizado_en": datetime(2026, 1, 1),
    }
    documento.update(campos)
    return documento


PAYLOAD_COMPLETO = {
    "nombre": "Capuccino de Especialidad",
    "descripcion": "Mezcla de especialidad con notas a chocolate y avellana.",
    "precio": 4500,
    "stock_fisico": 20,
    "imagenes": [
        "https://imagenes.cafe/capuccino/1.jpg",
        "https://imagenes.cafe/capuccino/2.jpg",
        "https://imagenes.cafe/capuccino/3.jpg",
        "https://imagenes.cafe/capuccino/4.jpg",
    ],
}


class BaseProductosMongoTests(APITestCase):
    def setUp(self):
        self.mongo = _BaseMongoFalsa()
        parche = patch("api.productos_service.get_mongo_db", return_value=self.mongo)
        parche.start()
        self.addCleanup(parche.stop)

        self.admin = User.objects.create_user(
            "admin@cafe.cl", email="admin@cafe.cl", password="AdminPassword123!", is_staff=True
        )
        self.cliente = User.objects.create_user(
            "cliente@cafe.cl", email="cliente@cafe.cl", password="Password123!"
        )

    @property
    def coleccion_productos(self):
        return self.mongo["productos"]


class CatalogoProductosTests(BaseProductosMongoTests):
    def test_paginacion_cincuenta_maximo_y_sin_perdidas(self):
        for i in range(55):
            self.coleccion_productos.insert_one(_producto_fake(i))

        url = reverse("productos_catalogo")
        pagina_1 = self.client.get(url, {"pagina": 1, "tamano": 50})
        self.assertEqual(pagina_1.status_code, 200)
        self.assertEqual(len(pagina_1.data["productos"]), 50)
        paginacion = pagina_1.data["paginacion"]
        self.assertEqual(paginacion["total"], 55)
        self.assertEqual(paginacion["total_paginas"], 2)
        self.assertTrue(paginacion["hay_siguiente"])
        self.assertFalse(paginacion["hay_anterior"])

        pagina_2 = self.client.get(url, {"pagina": 2, "tamano": 50})
        self.assertEqual(pagina_2.status_code, 200)
        self.assertEqual(len(pagina_2.data["productos"]), 5)
        self.assertTrue(pagina_2.data["paginacion"]["hay_anterior"])

        # Sin duplicados ni pérdidas entre páginas
        ids = (
            [p["identificador"] for p in pagina_1.data["productos"]]
            + [p["identificador"] for p in pagina_2.data["productos"]]
        )
        self.assertEqual(len(ids), len(set(ids)))

    def test_tamano_mayor_a_cincuenta_rechazado_rnf03(self):
        respuesta = self.client.get(reverse("productos_catalogo"), {"tamano": 51})
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("tamano", respuesta.data["errores"])

    def test_pagina_invalida_rechazada(self):
        for valor in ("0", "abc"):
            respuesta = self.client.get(reverse("productos_catalogo"), {"pagina": valor})
            self.assertEqual(respuesta.status_code, 400)
            self.assertIn("pagina", respuesta.data["errores"])

    def test_catalogo_excluye_inactivos_y_marca_agotados(self):
        self.coleccion_productos.insert_one(_producto_fake(1))
        self.coleccion_productos.insert_one(_producto_fake(2, estado="inactivo"))
        self.coleccion_productos.insert_one(_producto_fake(3, stock_fisico=0))

        respuesta = self.client.get(reverse("productos_catalogo"))
        self.assertEqual(respuesta.status_code, 200)
        productos = {p["identificador"]: p for p in respuesta.data["productos"]}
        self.assertIn("producto-1", productos)
        self.assertNotIn("producto-2", productos)
        # Stock cero = agotado, pero visible en el catálogo
        self.assertTrue(productos["producto-3"]["agotado"])
        self.assertFalse(productos["producto-3"]["disponible"])
        self.assertEqual(productos["producto-1"]["imagen_principal"],
                         "https://imagenes.cafe/1/0.jpg")
        self.assertEqual(productos["producto-1"]["moneda"], "CLP")

    def test_vista_gestion_requiere_administrador(self):
        self.coleccion_productos.insert_one(_producto_fake(1, estado="inactivo"))
        url = reverse("productos_catalogo")

        anonima = self.client.get(url, {"todos": 1})
        self.assertEqual(anonima.status_code, 403)

        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.get(url, {"todos": 1}).status_code, 403)

        self.client.force_authenticate(self.admin)
        gestion = self.client.get(url, {"todos": 1})
        self.assertEqual(gestion.status_code, 200)
        self.assertEqual(gestion.data["paginacion"]["total"], 1)

    def test_detalle_producto(self):
        self.coleccion_productos.insert_one(_producto_fake(1))
        self.coleccion_productos.insert_one(_producto_fake(2, estado="inactivo"))

        encontrado = self.client.get(
            reverse("producto_detalle", args=["producto-1"])
        )
        self.assertEqual(encontrado.status_code, 200)
        self.assertEqual(encontrado.data["producto"]["nombre"], "Producto 1")

        inexistente = self.client.get(
            reverse("producto_detalle", args=["no-existe"])
        )
        self.assertEqual(inexistente.status_code, 404)

        # Inactivo: oculto para público, visible para administración
        self.assertEqual(
            self.client.get(reverse("producto_detalle", args=["producto-2"])).status_code, 404
        )
        self.client.force_authenticate(self.admin)
        self.assertEqual(
            self.client.get(reverse("producto_detalle", args=["producto-2"])).status_code, 200
        )


class GestionProductosTests(BaseProductosMongoTests):
    def test_creacion_protegida_por_roles(self):
        url = reverse("productos_catalogo")
        self.assertEqual(self.client.post(url, PAYLOAD_COMPLETO, format="json").status_code, 401)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post(url, PAYLOAD_COMPLETO, format="json").status_code, 403)

    def test_creacion_valida(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(
            reverse("productos_catalogo"), PAYLOAD_COMPLETO, format="json"
        )
        self.assertEqual(respuesta.status_code, 201)
        producto = respuesta.data["producto"]
        self.assertTrue(producto["identificador"])
        self.assertEqual(producto["moneda"], "CLP")
        self.assertEqual(producto["estado"], "activo")
        self.assertEqual(producto["stock_reservado"], 0)
        self.assertTrue(producto["creado_en"])
        self.assertTrue(producto["actualizado_en"])
        # RF-16: validación de nombre y descripción no vacíos, precio > 0,
        # stock entero >= 0 y entre 4 y 6 imágenes.
        self.assertEqual(self.coleccion_productos.count_documents({}), 1)

    def test_creacion_validaciones_por_campo(self):
        self.client.force_authenticate(self.admin)
        url = reverse("productos_catalogo")

        casos = [
            ({**PAYLOAD_COMPLETO, "nombre": "  "}, "nombre"),
            ({**PAYLOAD_COMPLETO, "precio": 0}, "precio"),
            ({**PAYLOAD_COMPLETO, "precio": -100}, "precio"),
            ({**PAYLOAD_COMPLETO, "stock_fisico": -1}, "stock_fisico"),
            ({**PAYLOAD_COMPLETO, "stock_fisico": 2.5}, "stock_fisico"),
            ({**PAYLOAD_COMPLETO, "imagenes": PAYLOAD_COMPLETO["imagenes"][:2]}, "imagenes"),
        ]
        for payload, campo in casos:
            with self.subTest(campo=campo, valor=payload.get(campo)):
                respuesta = self.client.post(url, payload, format="json")
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn(campo, respuesta.data["errores"])
        self.assertEqual(self.coleccion_productos.count_documents({}), 0)

    def test_edicion_respetando_identificador_inmutable(self):
        self.coleccion_productos.insert_one(_producto_fake(1))
        self.client.force_authenticate(self.admin)

        ok = self.client.put(
            reverse("producto_detalle", args=["producto-1"]),
            {"nombre": "Nuevo nombre", "precio": 5990},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.data["producto"]["nombre"], "Nuevo nombre")
        self.assertEqual(ok.data["producto"]["precio"], 5990)
        self.assertEqual(ok.data["producto"]["identificador"], "producto-1")

        inmutable = self.client.put(
            reverse("producto_detalle", args=["producto-1"]),
            {"identificador": "otro-identificador"},
            format="json",
        )
        self.assertEqual(inmutable.status_code, 400)
        self.assertIn("identificador", inmutable.data["errores"])

        # El stock no se edita por esta vía
        por_via_equivocada = self.client.put(
            reverse("producto_detalle", args=["producto-1"]),
            {"stock_fisico": 999},
            format="json",
        )
        self.assertEqual(por_via_equivocada.status_code, 400)

    def test_desactivar_sin_eliminar(self):
        self.coleccion_productos.insert_one(_producto_fake(1))
        self.client.force_authenticate(self.admin)

        respuesta = self.client.patch(
            reverse("producto_estado", args=["producto-1"]),
            {"estado": "inactivo"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["producto"]["estado"], "inactivo")
        # RF-18: el documento sigue existiendo en MongoDB
        self.assertIsNotNone(self.coleccion_productos.find_one({"identificador": "producto-1"}))

        invalido = self.client.patch(
            reverse("producto_estado", args=["producto-1"]),
            {"estado": "borrado"},
            format="json",
        )
        self.assertEqual(invalido.status_code, 400)

    def test_ajuste_de_stock_con_auditoria(self):
        self.coleccion_productos.insert_one(
            _producto_fake(1, stock_fisico=10, stock_reservado=4)
        )
        self.client.force_authenticate(self.admin)
        url = reverse("producto_stock", args=["producto-1"])

        ok = self.client.patch(url, {"stock_fisico": 8}, format="json")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.data["producto"]["stock_fisico"], 8)

        # Registro de auditoría: producto, valor anterior, valor nuevo, admin, fecha
        auditorias = self.mongo["ajustes_stock"].documentos
        self.assertEqual(len(auditorias), 1)
        registro = auditorias[0]
        self.assertEqual(registro["producto_identificador"], "producto-1")
        self.assertEqual(registro["valor_anterior"], 10)
        self.assertEqual(registro["valor_nuevo"], 8)
        self.assertEqual(registro["administrador"]["id"], self.admin.pk)
        self.assertTrue(registro["fecha"])

        # RF-19: entero >= 0 y nunca menor al stock reservado
        bajo_reservado = self.client.patch(url, {"stock_fisico": 3}, format="json")
        self.assertEqual(bajo_reservado.status_code, 400)
        self.assertIn("stock_fisico", bajo_reservado.data["errores"])

        negativo = self.client.patch(url, {"stock_fisico": -1}, format="json")
        self.assertEqual(negativo.status_code, 400)

        no_entero = self.client.patch(url, {"stock_fisico": 7.5}, format="json")
        self.assertEqual(no_entero.status_code, 400)

        # Solo el ajuste válido quedó auditado
        self.assertEqual(len(self.mongo["ajustes_stock"].documentos), 1)
