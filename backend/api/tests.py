from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


class PanelAdminTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user('admin', password='test-password', is_staff=True)
        self.cliente = User.objects.create_user('cliente', email='cliente@example.com')
        self.otro_admin = User.objects.create_user('otro_admin', is_staff=True)
        self.lista = reverse('usuarios_admin')

    def editar(self, usuario, datos):
        return self.client.patch(reverse('editar_usuario_admin', args=[usuario.pk]), datos, format='json')

    def test_acceso_solo_administradores(self):
        self.assertEqual(self.client.get(self.lista).status_code, 403)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.get(self.lista).status_code, 403)
        self.assertEqual(self.editar(self.otro_admin, {'first_name': 'Intruso'}).status_code, 403)

    def test_lista_identifica_cuenta_actual_y_roles(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.lista)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['usuario_actual_id'], self.admin.pk)
        roles = {u['id']: u['rol'] for u in response.data['usuarios']}
        self.assertEqual(roles[self.cliente.pk], 'cliente')
        self.assertEqual(roles[self.otro_admin.pk], 'admin')
        self.assertNotIn('password', response.data['usuarios'][0])

    def test_suspender_cliente_y_otro_administrador(self):
        self.client.force_authenticate(self.admin)
        for usuario in [self.cliente, self.otro_admin]:
            with self.subTest(usuario=usuario.username):
                url = reverse('suspender_usuario_admin', args=[usuario.pk])
                self.assertEqual(self.client.post(url).status_code, 200)
                usuario.refresh_from_db()
                self.assertFalse(usuario.is_active)
                self.assertTrue(get_user_model().objects.filter(pk=usuario.pk).exists())
                self.assertEqual(self.client.post(url).status_code, 200)

    def test_suspension_restringida_y_cuenta_propia_protegida(self):
        url = reverse('suspender_usuario_admin', args=[self.otro_admin.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_authenticate(self.admin)
        propia = reverse('suspender_usuario_admin', args=[self.admin.pk])
        self.assertEqual(self.client.post(propia).status_code, 403)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertEqual(self.editar(self.cliente, {'is_active': False}).status_code, 400)

    def test_administrador_suspendido_pierde_acceso_y_sesion(self):
        session_client = APIClient()
        session_client.force_login(self.otro_admin)
        self.assertEqual(session_client.get(self.lista).status_code, 200)
        self.client.force_authenticate(self.admin)
        url = reverse('suspender_usuario_admin', args=[self.otro_admin.pk])
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(session_client.get(self.lista).status_code, 403)
        self.otro_admin.refresh_from_db()
        self.client.force_authenticate(self.otro_admin)
        self.assertEqual(self.client.get(self.lista).status_code, 403)
        self.assertEqual(self.client.post(reverse('suspender_usuario_admin', args=[self.cliente.pk])).status_code, 403)

    def test_suspension_requiere_csrf_y_usuario_existente(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse('suspender_usuario_admin', args=[self.cliente.pk])
        self.assertEqual(client.post(url).status_code, 403)
        token = client.get(self.lista).data['csrf_token']
        self.assertEqual(client.post(url, HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.assertEqual(client.post(reverse('suspender_usuario_admin', args=[999999]), HTTP_X_CSRFTOKEN=token).status_code, 404)
    def test_editar_cliente_y_otro_admin(self):
        self.client.force_authenticate(self.admin)
        for usuario in [self.cliente, self.otro_admin]:
            with self.subTest(usuario=usuario.username):
                response = self.editar(usuario, {'first_name': 'Nuevo', 'last_name': 'Apellido', 'email': f'{usuario.username}@example.com'})
                self.assertEqual(response.status_code, 200)
                usuario.refresh_from_db()
                self.assertEqual(usuario.first_name, 'Nuevo')

    def test_no_editar_cuenta_propia_ni_permisos(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.editar(self.admin, {'first_name': 'Nuevo'}).status_code, 403)
        self.assertEqual(self.editar(self.cliente, {'is_staff': True}).status_code, 400)
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_staff)

    def test_validar_correo_y_nombre(self):
        self.client.force_authenticate(self.admin)
        for datos in [{'email': 'invalido'}, {'first_name': ' '}, {'email': 'CLIENTE@example.com'}]:
            with self.subTest(datos=datos):
                self.assertEqual(self.editar(self.otro_admin, datos).status_code, 400)
        self.assertEqual(self.editar(self.cliente, {'email': self.cliente.email}).status_code, 200)

    def test_reactivar_cliente_y_admin_conserva_datos_y_rol(self):
        self.client.force_authenticate(self.admin)
        for usuario in [self.cliente, self.otro_admin]:
            with self.subTest(usuario=usuario.username):
                self.client.post(reverse('suspender_usuario_admin', args=[usuario.pk]))
                response = self.client.post(reverse('activar_usuario_admin', args=[usuario.pk]))
                self.assertEqual(response.status_code, 200)
                usuario.refresh_from_db()
                self.assertTrue(usuario.is_active)
                self.assertEqual(response.data['email'], usuario.email)
                self.assertEqual(response.data['rol'], 'admin' if usuario.is_staff else 'cliente')
        session_client = APIClient()
        session_client.force_login(self.otro_admin)
        self.assertEqual(session_client.get(self.lista).status_code, 200)

    def test_activacion_restringida_y_requiere_csrf(self):
        url = reverse('activar_usuario_admin', args=[self.cliente.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post(reverse('activar_usuario_admin', args=[self.admin.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('activar_usuario_admin', args=[999999])).status_code, 404)
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.admin)
        self.assertEqual(client.post(url).status_code, 403)
        token = client.get(self.lista).data['csrf_token']
        self.assertEqual(client.post(url, HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.otro_admin.is_active = False
        self.otro_admin.save(update_fields=['is_active'])
        self.client.force_authenticate(self.otro_admin)
        self.assertEqual(self.client.post(url).status_code, 403)

    def test_sesion_requiere_csrf_para_guardar(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse('editar_usuario_admin', args=[self.cliente.pk])
        self.assertEqual(client.patch(url, {'first_name': 'Nuevo'}, format='json').status_code, 403)
        token = client.get(self.lista).data['csrf_token']
        response = client.patch(url, {'first_name': 'Nuevo'}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
