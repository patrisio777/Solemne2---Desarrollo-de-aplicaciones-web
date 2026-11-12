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
        resp = self.client.post('/api/registro/', datos_incompletos, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Caso B: Formato de correo inválido
        datos_correo_malo = {'email': 'correo-no-valido', 'password': 'PasswordSegura123!'}
        resp = self.client.post('/api/registro/', datos_correo_malo, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Caso C: Contraseña demasiado débil o corta
        datos_clave_corta = {'email': 'valido@cafe.cl', 'password': '123'}
        resp = self.client.post('/api/registro/', datos_clave_corta, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- PRUEBA 2: Rechazo de login con credenciales incorrectas ---
    def test_login_credenciales_incorrectas(self):
        # Contraseña equivocada
        datos = {'email': 'cliente@cafe.cl', 'password': 'ClaveErronea123'}
        resp = self.client.post('/api/login/', datos, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(resp.data.get('error'), 'Datos incorrectos.')

        # Correo inexistente
        datos_no_existe = {'email': 'fantasma@cafe.cl', 'password': 'Password123!'}
        resp = self.client.post('/api/login/', datos_no_existe, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PRUEBA 3: Rechazo de login para cuentas bloqueadas ---
    def test_login_cuenta_bloqueada(self):
        datos = {'email': 'bloqueado@cafe.cl', 'password': 'Password123!'}
        resp = self.client.post('/api/login/', datos, format='json')
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


# ==============================================================================
# PRUEBAS DE GESTIÓN DE USUARIOS (HU-08)
# Creación, consulta individual/general, edición, bloqueo y restricciones de seguridad
# ==============================================================================
class PruebasGestionUsuarios(APITestCase):

    def setUp(self):
        # 1. Administrador principal (quien ejecuta las acciones)
        self.admin = User.objects.create_user(
            username='admin_gestor@cafe.cl',
            email='admin_gestor@cafe.cl',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='Gestor',
            is_staff=True,
            is_active=True
        )
        self.token_admin = Token.objects.create(user=self.admin)

        # 2. Segundo administrador (para verificar operaciones entre administradores)
        self.admin_secundario = User.objects.create_user(
            username='admin_segundo@cafe.cl',
            email='admin_segundo@cafe.cl',
            password='AdminPassword123!',
            first_name='Segundo',
            last_name='Admin',
            is_staff=True,
            is_active=True
        )

        # 3. Superusuario del sistema
        self.superuser = User.objects.create_superuser(
            username='superadmin@cafe.cl',
            email='superadmin@cafe.cl',
            password='SuperPassword123!'
        )

        # 4. Usuario cliente estándar
        self.cliente = User.objects.create_user(
            username='cliente_prueba@cafe.cl',
            email='cliente_prueba@cafe.cl',
            password='ClientePassword123!',
            first_name='Carlos',
            last_name='Soto',
            is_staff=False,
            is_active=True
        )
        self.token_cliente = Token.objects.create(user=self.cliente)

    # --- 1. ACCESO NO AUTORIZADO (Sin Token y Rol Cliente) ---
    def test_gestion_usuarios_acceso_no_autorizado(self):
        # A. Peticiones anónimas sin token -> 401 Unauthorized
        self.client.credentials()  # Sin credenciales
        self.assertEqual(self.client.get('/api/users/').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post('/api/users/', {}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(f'/api/users/{self.cliente.id}/').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(f'/api/users/{self.cliente.id}/', {}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)

        # B. Peticiones con rol Cliente (no admin) -> 403 Forbidden
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_cliente.key)
        self.assertEqual(self.client.get('/api/users/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.post('/api/users/', {}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(f'/api/users/{self.cliente.id}/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(f'/api/users/{self.cliente.id}/', {}, format='json').status_code, status.HTTP_403_FORBIDDEN)

    # --- 2. LISTADO DE USUARIOS (GET /api/users/) ---
    def test_listar_usuarios_exitoso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp = self.client.get('/api/users/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('status'), 'success')
        self.assertGreaterEqual(resp.data.get('total'), 4)
        self.assertIsInstance(resp.data.get('data'), list)

    # --- 3. CREACIÓN INDIVIDUAL DE USUARIOS (POST /api/users/) ---
    def test_crear_usuario_exitoso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        nuevo_usuario_data = {
            'email': 'nuevo_barista@cafe.cl',
            'password': 'PasswordSegura2026!',
            'nombre': 'Valeria',
            'apellido': 'Rojas',
            'es_admin': True
        }
        resp = self.client.post('/api/users/', nuevo_usuario_data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('status'), 'success')
        self.assertEqual(resp.data.get('usuario', {}).get('email'), 'nuevo_barista@cafe.cl')
        self.assertTrue(resp.data.get('usuario', {}).get('es_admin'))
        self.assertTrue(User.objects.filter(email='nuevo_barista@cafe.cl').exists())

    def test_crear_usuario_validaciones_error(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)

        # Caso A: Faltan datos obligatorios (sin contraseña)
        resp_sin_pass = self.client.post('/api/users/', {'email': 'sinpass@cafe.cl'}, format='json')
        self.assertEqual(resp_sin_pass.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Faltan datos obligatorios', resp_sin_pass.data.get('message', ''))

        # Caso B: Formato de correo inválido
        resp_correo_malo = self.client.post('/api/users/', {'email': 'formato-invalido', 'password': 'Password123!'}, format='json')
        self.assertEqual(resp_correo_malo.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('formato válido', resp_correo_malo.data.get('message', ''))

        # Caso C: Correo ya registrado (duplicado)
        resp_duplicado = self.client.post('/api/users/', {
            'email': 'cliente_prueba@cafe.cl',
            'password': 'Password123!'
        }, format='json')
        self.assertEqual(resp_duplicado.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ya se encuentra registrado', resp_duplicado.data.get('message', ''))

        # Caso D: Contraseña débil
        resp_pass_debil = self.client.post('/api/users/', {
            'email': 'usuario_debil@cafe.cl',
            'password': '123'
        }, format='json')
        self.assertEqual(resp_pass_debil.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 4. CONSULTA INDIVIDUAL POR ID (GET /api/users/<id>/) ---
    def test_consultar_usuario_individual_exitoso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp = self.client.get(f'/api/users/{self.cliente.id}/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('status'), 'success')
        self.assertEqual(resp.data.get('usuario', {}).get('id'), self.cliente.id)
        self.assertEqual(resp.data.get('usuario', {}).get('email'), self.cliente.email)
        self.assertIn('fecha_registro', resp.data.get('usuario', {}))

    def test_consultar_usuario_no_encontrado(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp = self.client.get('/api/users/99999/')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data.get('status'), 'error')

    # --- 5. EDICIÓN DE USUARIOS (PATCH /api/users/<id>/) ---
    def test_editar_datos_usuario_exitoso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        datos_actualizar = {
            'first_name': 'Carlos Modificado',
            'last_name': 'Soto Actualizado',
            'email': 'carlos_nuevo@cafe.cl'
        }
        resp = self.client.patch(f'/api/users/{self.cliente.id}/', datos_actualizar, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('status'), 'success')
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.first_name, 'Carlos Modificado')
        self.assertEqual(self.cliente.email, 'carlos_nuevo@cafe.cl')

    def test_editar_usuario_validaciones_email(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)

        # Formato inválido
        resp_malo = self.client.patch(f'/api/users/{self.cliente.id}/', {'email': 'no-es-correo'}, format='json')
        self.assertEqual(resp_malo.status_code, status.HTTP_400_BAD_REQUEST)

        # Email duplicado (pertenece a otro usuario)
        resp_duplicado = self.client.patch(f'/api/users/{self.cliente.id}/', {'email': self.admin.email}, format='json')
        self.assertEqual(resp_duplicado.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ya está registrado', resp_duplicado.data.get('message', ''))

    # --- 6. BLOQUEO / SUSPENSIÓN Y RESTRICCIONES DE SEGURIDAD (PATCH /api/users/<id>/) ---
    def test_bloquear_y_desbloquear_usuario_cliente(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)

        # Bloquear
        resp_bloqueo = self.client.patch(f'/api/users/{self.cliente.id}/', {'is_active': False}, format='json')
        self.assertEqual(resp_bloqueo.status_code, status.HTTP_200_OK)
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_active)

        # Desbloquear
        resp_desbloqueo = self.client.patch(f'/api/users/{self.cliente.id}/', {'is_active': True}, format='json')
        self.assertEqual(resp_desbloqueo.status_code, status.HTTP_200_OK)
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.is_active)

    def test_seguridad_prevenir_autobloqueo_administrador(self):
        # Regla 1: Un administrador no puede auto-suspender su cuenta
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp = self.client.patch(f'/api/users/{self.admin.id}/', {'is_active': False}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('propia cuenta', resp.data.get('message', ''))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_seguridad_prevenir_bloqueo_superusuario(self):
        # Regla 2: No se puede suspender a un superusuario
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)
        resp = self.client.patch(f'/api/users/{self.superuser.id}/', {'is_active': False}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('superusuario', resp.data.get('message', ''))
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_active)

    def test_seguridad_prevenir_bloqueo_ultimo_admin_activo(self):
        # Regla 3: No se puede suspender al último administrador activo
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_admin.key)

        # Aseguramos que solo self.admin y self.admin_secundario sean los únicos staff
        self.superuser.is_staff = False
        self.superuser.save()

        # Suspender a admin_secundario (ahora queda solo 1 admin activo: self.admin)
        resp_suspender_segundo = self.client.patch(
            f'/api/users/{self.admin_secundario.id}/',
            {'is_active': False},
            format='json'
        )
        self.assertEqual(resp_suspender_segundo.status_code, status.HTTP_200_OK)
        self.admin_secundario.refresh_from_db()
        self.assertFalse(self.admin_secundario.is_active)

        # Intentar volver a mandar suspensión a admin_secundario cuando ya solo queda 1 admin activo
        resp_ultimo = self.client.patch(
            f'/api/users/{self.admin_secundario.id}/',
            {'is_active': False},
            format='json'
        )
        self.assertEqual(resp_ultimo.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('último administrador activo', resp_ultimo.data.get('message', ''))
