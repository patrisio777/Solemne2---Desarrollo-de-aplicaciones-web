"""
Pruebas del Sprint 4: tema visual activo y mensajes de contacto en PostgreSQL
(HU-06 / RF-04 y HU-07 / RF-05), más la auditoría de inicios de sesión en
MongoDB (Reglas de Seguridad del Sprint 2).
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import MensajeContacto, TemaVisual


class TemaVisualTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            "admin@cafe.cl", email="admin@cafe.cl", password="AdminPassword123!", is_staff=True
        )
        self.cliente = get_user_model().objects.create_user(
            "cliente@cafe.cl", email="cliente@cafe.cl", password="Password123!"
        )
        self.url = reverse("tema_activo")

    def test_tema_activo_por_defecto_es_claro(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["tema"]["nombre"], "claro")
        # Los cuatro temas aprobados quedan creados
        self.assertEqual(TemaVisual.objects.count(), 4)

    def test_guardar_tema_valido_persiste(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {"nombre": "vintage"}, format="json")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["tema"]["nombre"], "vintage")

        # Persiste en PostgreSQL: una consulta nueva lo confirma
        consulta = self.client.get(self.url)
        self.assertEqual(consulta.data["tema"]["nombre"], "vintage")

        # Solo un tema activo a la vez
        activos = TemaVisual.objects.filter(activo=True)
        self.assertEqual(activos.count(), 1)
        self.assertEqual(activos.first().nombre, "vintage")

    def test_rechaza_tema_fuera_de_los_cuatro_aprobados(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {"nombre": "neon"}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("claro", respuesta.data["message"])

    def test_rechaza_identificador_inexistente(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {"identificador": 99999}, format="json")
        self.assertEqual(respuesta.status_code, 404)
        self.assertIn("identificador", respuesta.data["message"])

    def test_cambiar_tema_requiere_administrador(self):
        # El GET público crea los cuatro temas y deja 'claro' activo
        self.assertEqual(self.client.get(self.url).data["tema"]["nombre"], "claro")

        anonima = self.client.post(self.url, {"nombre": "oscuro"}, format="json")
        self.assertEqual(anonima.status_code, 401)

        self.client.force_authenticate(self.cliente)
        cliente = self.client.post(self.url, {"nombre": "oscuro"}, format="json")
        self.assertEqual(cliente.status_code, 403)

        # El tema no cambió
        self.assertEqual(TemaVisual.objects.get(activo=True).nombre, "claro")

    def test_falta_el_tema_a_activar(self):
        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url, {}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("nombre", respuesta.data["errores"])


class MensajeContactoTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            "admin@cafe.cl", email="admin@cafe.cl", password="AdminPassword123!", is_staff=True
        )
        self.cliente = get_user_model().objects.create_user(
            "cliente@cafe.cl", email="cliente@cafe.cl", password="Password123!"
        )
        self.url = reverse("crear_mensaje_contacto")
        self.payload = {
            "nombre": "Francisca Silva",
            "email": "francisca@ejemplo.cl",
            "mensaje": "Quisiera cotizar una barra de cafe para un evento corporativo.",
        }

    def test_mensaje_valido_se_almacena(self):
        respuesta = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(MensajeContacto.objects.count(), 1)
        mensaje = MensajeContacto.objects.get()
        self.assertEqual(mensaje.nombre, "Francisca Silva")
        self.assertFalse(mensaje.leido)

    def test_errores_de_validacion_por_campo(self):
        casos = [
            ({**self.payload, "nombre": "A"}, "nombre"),
            ({**self.payload, "nombre": "x" * 101}, "nombre"),
            ({**self.payload, "email": "no-es-correo"}, "email"),
            ({**self.payload, "mensaje": "corto"}, "mensaje"),
            ({**self.payload, "mensaje": "x" * 2001}, "mensaje"),
        ]
        for payload, campo in casos:
            with self.subTest(campo=campo):
                respuesta = self.client.post(self.url, payload, format="json")
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn(campo, respuesta.data["errores"])
        self.assertEqual(MensajeContacto.objects.count(), 0)

    def test_no_informa_exito_si_falla_el_almacenamiento(self):
        with patch.object(
            MensajeContacto.objects, "create", side_effect=Exception("psql caido")
        ):
            respuesta = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(respuesta.data["status"], "error")

    def test_consulta_de_mensajes_solo_administradores(self):
        MensajeContacto.objects.create(**self.payload)
        url = reverse("listar_mensajes_contacto")

        self.assertEqual(self.client.get(url).status_code, 401)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_authenticate(self.admin)
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["total"], 1)
        self.assertEqual(respuesta.data["mensajes"][0]["email"], "francisca@ejemplo.cl")


class AuditoriaInicioSesionTests(APITestCase):
    """Registro de inicios de sesión en MongoDB Atlas (Sprint 2)."""

    def setUp(self):
        self.activo = get_user_model().objects.create_user(
            "otro@cafe.cl", email="otro@cafe.cl", password="Password123!"
        )
        get_user_model().objects.create_user(
            "cliente@cafe.cl", email="cliente@cafe.cl", password="Password123!"
        )
        get_user_model().objects.filter(username="cliente@cafe.cl").update(is_active=False)
        self.url = reverse("login")

    def test_inicio_exitoso_queda_registrado(self):
        with patch("api.auth_views.registrar_inicio_sesion") as registro:
            respuesta = self.client.post(
                self.url, {"email": "otro@cafe.cl", "password": "Password123!"}, format="json"
            )
        self.assertEqual(respuesta.status_code, 200)
        registro.assert_called_once()
        _, kwargs = registro.call_args
        self.assertTrue(kwargs["exito"])
        self.assertIsNone(kwargs.get("motivo"))

    def test_clave_incorrecta_y_cuenta_suspendida_se_registran(self):
        with patch("api.auth_views.registrar_inicio_sesion") as registro:
            self.client.post(
                self.url, {"email": "otro@cafe.cl", "password": "ClaveMala123!"}, format="json"
            )
        _, kwargs = registro.call_args
        self.assertFalse(kwargs["exito"])
        self.assertEqual(kwargs["motivo"], "clave_incorrecta")

        with patch("api.auth_views.registrar_inicio_sesion") as registro:
            respuesta = self.client.post(
                self.url, {"email": "cliente@cafe.cl", "password": "Password123!"}, format="json"
            )
        self.assertEqual(respuesta.status_code, 403)
        _, kwargs = registro.call_args
        self.assertFalse(kwargs["exito"])
        self.assertEqual(kwargs["motivo"], "cuenta_suspendida")

    def test_respuestas_sin_revelar_datos_internos(self):
        # Mismo mensaje para usuario inexistente y clave incorrecta
        inexistente = self.client.post(
            self.url, {"email": "nadie@cafe.cl", "password": "Password123!"}, format="json"
        )
        self.assertEqual(inexistente.status_code, 401)
        self.assertEqual(inexistente.data["error"], "Datos incorrectos.")
