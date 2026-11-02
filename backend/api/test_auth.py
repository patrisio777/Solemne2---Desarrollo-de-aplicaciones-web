from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

class PruebasAutenticacionYPermisos(APITestCase):

    def setUp(self):
        #Crear un usuario cliente normal para las pruebas
        self.cliente = User.objects.create_user(
            username='cliente@cafe.cl',
            email='cliente@cafe.cl',
            password='Password123!',
            first_name='Juan',
            last_name='Perez',
            is_staff=False
        )
        self.token_cliente = Token.objects.create(user=self.cliente)

        #Crear un usuario administrador
        self.admin = User.objects.create_user(
            username='admin@cafe.cl',
            email='admin@cafe.cl',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='Cafeteria',
            is_staff=True
        )
        self.token_admin = Token.objects.create(user=self.admin)

        #Crear un usuario suspendido (is_active = False)
        self.bloqueado = User.objects.create_user(
            username='bloqueado@cafe.cl',
            email='bloqueado@cafe.cl',
            password='Password123!',
            is_active=False
        )

    # --- PRUEBA 1: Rechazo de registros con campos inválidos ---
    def test_registro_campos_invalidos_o_faltantes(self):
        # Caso A: Falta contraseña
        datos_incompletos = {'email': 'incompleto@cafe.cl'}
        resp = self.client.post('/api/registro/', datos_incompletos)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Caso B: Formato de correo inválido
        datos_correo_malo = {'email': 'correo-no-valido', 'password': 'PasswordSegura123!'}
        resp = self.client.post('/api/registro/', datos_correo_malo)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Caso C: Contraseña demasiado débil o corta
        datos_clave_corta = {'email': 'valido@cafe.cl', 'password': '123'}
        resp = self.client.post('/api/registro/', datos_clave_corta)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- PRUEBA 2: Rechazo de login con credenciales incorrectas ---
    def test_login_credenciales_incorrectas(self):
        # Contraseña equivocada
        datos = {'email': 'cliente@cafe.cl', 'password': 'ClaveErronea123'}
        resp = self.client.post('/api/login/', datos)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.data.get('error'), 'Datos incorrectos.')

        # Correo inexistente
        datos_no_existe = {'email': 'fantasma@cafe.cl', 'password': 'Password123!'}
        resp = self.client.post('/api/login/', datos_no_existe)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PRUEBA 3: Rechazo de login para cuentas bloqueadas ---
    def test_login_cuenta_bloqueada(self):
        datos = {'email': 'bloqueado@cafe.cl', 'password': 'Password123!'}
        resp = self.client.post('/api/login/', datos)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('suspendida', resp.data.get('error', '').lower())

    # --- PRUEBA 4: Control de permisos y roles en endpoints protegidos ---
    def test_autorizacion_por_roles(self):
        # Caso A: Intento de acceso sin token (Anónimo) -> 401 Unauthorized
        resp = self.client.get('/api/admin-panel/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Caso B: Cliente intentando acceder a panel de Administrador -> 403 Forbidden
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_cliente.key)
        resp_cliente_en_admin = self.client.get('/api/admin-panel/')
        self.assertEqual(resp_cliente_en_admin.status_code, status.HTTP_403_FORBIDDEN)

        # Caso C: Cliente accediendo a su propio perfil -> 200 OK
        resp_cliente_perfil = self.client.get('/api/perfil/')
        self.assertEqual(resp_cliente_perfil.status_code, status.HTTP_200_OK)

        # Caso D: Administrador accediendo a panel de administración -> 200 OK
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp_admin_en_admin = self.client.get('/api/admin-panel/')
        self.assertEqual(resp_admin_en_admin.status_code, status.HTTP_200_OK)