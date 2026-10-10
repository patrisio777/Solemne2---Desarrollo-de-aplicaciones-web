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
