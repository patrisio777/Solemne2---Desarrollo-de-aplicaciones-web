# Frontend - Cafetería

Interfaz de la tienda hecha con React + Vite.

## Requisitos

- Node.js (versión LTS)
- npm (viene con Node.js)

## Cómo ejecutarlo

Desde la carpeta `frontend`:

```bash
npm install
npm run dev
```

Luego abrir http://localhost:5173 en el navegador.

## Comandos

| Comando | Qué hace |
|---|---|
| `npm run dev` | Levanta el proyecto en modo desarrollo |
| `npm run build` | Genera la versión para publicar en la carpeta `dist` |
| `npm run preview` | Muestra la versión generada con `build` |
| `npm run lint` | Revisa el código con ESLint |

## Estructura

```
src/
  components/   Navbar y Footer
  pages/        Una página por ruta
  App.jsx       Rutas de la aplicación
  main.jsx      Punto de entrada
```

## Rutas

| Ruta | Página |
|---|---|
| `/` | Inicio |
| `/catalogo` | Catálogo |
| `/producto/:id` | Detalle de producto |
| `/carrito` | Carrito |
| `/login` | Iniciar sesión |
| `/registro` | Registro |
| `/pago` | Pago |
| `/confirmacion` | Confirmación |
| `/contacto` | Contacto |
| `/quienes-somos` | Quiénes somos |
| cualquier otra | Página no encontrada |

## Administración de usuarios conectada

Compatible con el contrato de [dwebs03BackendCafein-manos](https://github.com/ReneGG/dwebs03BackendCafein-manos) revisado en el commit `798656f`.

1. Inicia ese backend según su documentación, configura su base de datos y ejecuta sus migraciones. Crea una cuenta con permisos de administrador (`is_staff=True`, por ejemplo mediante `python manage.py createsuperuser`).
2. Copia `.env.example` a `.env` y configura `VITE_API_URL=http://localhost:8000/api` (sin `/` final). Reinicia Vite después de cambiar esta variable.
3. En el backend permite el origen del frontend en `CORS_ALLOWED_ORIGINS`, por ejemplo `http://127.0.0.1:5173` y `http://localhost:5173`.
4. Inicia sesión en `/login` con el correo y la contraseña de la cuenta real. `/admin` consultará los usuarios del servidor.

La integración envía `Authorization: Token <token>` y utiliza:

| Acción | Petición |
|---|---|
| Listar | `GET /api/users/` → `{status, total, data: [...]}` |
| Consultar | `GET /api/users/<id>/` → `{status, usuario}` |
| Crear cliente | `POST /api/users/` con `first_name`, `last_name`, `email`, `password` y `es_admin: false` |
| Editar | `PATCH /api/users/<id>/` con `first_name`, `last_name` y `email` |
| Bloquear/reactivar | `PATCH /api/users/<id>/` con `is_active: false/true` |

Las respuestas de creación y actualización usan `{status, message, usuario}`. Los errores del backend se muestran sin aplicar cambios locales. La cuenta propia se identifica por el correo devuelto al iniciar sesión y no se puede editar ni suspender desde la tabla. El servidor decide las restricciones de superusuarios y del último administrador activo.

`admin1/admin1` es únicamente una sesión de demostración en desarrollo y no obtiene un token del backend. `/demo/admin` también usa datos locales; incluye creación, consulta, edición y cambios de estado que se restablecen al recargar. Los productos continúan en modo demostración.
