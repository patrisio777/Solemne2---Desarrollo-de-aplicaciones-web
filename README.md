# Solemne2---Desarrollo-de-aplicaciones-web

## Panel de control de usuarios

Disponible en `/panel-admin`. Permite listar y buscar clientes y administradores,
filtrar por tipo de cuenta y editar nombre, apellido y correo electrónico.
La cuenta conectada no se puede editar desde este panel. El servidor impide
cambiar roles, nombres de usuario y contraseñas.

1. Preparar el backend siguiendo `backend/instalar_dependencias.md`.
2. Crear una cuenta administrativa con `python manage.py createsuperuser`.
3. Iniciar Django con `python manage.py runserver`.
4. En `frontend`, ejecutar `npm ci` y `npm run dev`.
5. Abrir `/panel-admin` en Vite e iniciar sesión con el enlace de administrador.
   Se usa temporalmente el login de Django porque el login de la tienda todavía
   no está implementado. Para crear otros usuarios se puede usar Django admin.

Se considera administrador a un usuario con `is_staff` o `is_superuser`.
Vite redirige `/api` y `/admin` al backend local para compartir sesión y CSRF.
En producción, configurar estas rutas bajo el mismo dominio.

Verificación: `npm run lint`, `npm run build` y `python manage.py test api`.

Para preparar los usuarios ficticios de la cafetería en desarrollo, ejecutar
`python manage.py preparar_demo_cafeteria`. Patricio Chaung y Cristobal Garrido
son administradores; Gabriel Moreno, Brandon Valdés, Javiera Fuentealba y Jose
Arguello son clientes. Sus correos `example.com` son de demostración.
Este comando conserva las contraseñas de las cuentas de demo existentes;
las nuevas cuentas no tienen contraseña de acceso. No modifica otras cuentas.

El panel se verificó localmente con Python 3.12, Django 5.2.18 y Django REST
Framework 3.18.3. Las versiones declaradas en `backend/requerimientos.md`
se conservan; las pruebas deberán repetirse en ese entorno antes de desplegar.
