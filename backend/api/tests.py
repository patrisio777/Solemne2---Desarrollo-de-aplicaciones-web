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

    def test_sesion_requiere_csrf_para_guardar(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse('editar_usuario_admin', args=[self.cliente.pk])
        self.assertEqual(client.patch(url, {'first_name': 'Nuevo'}, format='json').status_code, 403)
        token = client.get(self.lista).data['csrf_token']
        response = client.patch(url, {'first_name': 'Nuevo'}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
