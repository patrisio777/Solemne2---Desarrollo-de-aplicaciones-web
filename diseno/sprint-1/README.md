# Sprint 1 · Paraíso del Café

Autor: Cristóbal Garrido. Entregables de diseño, sin funcionalidades del Sprint 2.

Abrir `index.html` en un navegador: incluye identidad, diez bocetos navegables y
comparación de los temas Claro, Oscuro, Vintage y Pastel. No requiere instalar
dependencias. Puede servirse con `python -m http.server 5175 --bind 127.0.0.1`
desde esta carpeta. Los SVG se pueden descargar desde la presentación.

## Identidad

Nombre confirmado: Paraíso del Café. Frase propuesta: «Un sorbo al paraíso».
El símbolo representa varios granos de café bajo una palmera. Carácter: artesanal y acogedor, un espacio para relajarse. Usar el logotipo
horizontal en encabezados y el símbolo independiente en espacios reducidos.
Archivos: `logotipo.svg` y `simbolo.svg`.

Mantener margen libre equivalente al ancho del grano. Símbolo mínimo recomendado:
32 px; logotipo completo: 220 px. No deformar, rotar ni añadir sombras al logo.
En fondos oscuros usar una versión clara del símbolo con el color de texto del tema.
El logotipo usa texto SVG: para entrega de imprenta convertir las letras a contornos.

Tipografía: Georgia para títulos y Trebuchet MS para interfaz; alternativas serif
y sans-serif locales. Escala: títulos 44/30/22 px; cuerpo 16 px; controles 14 px;
etiquetas 12 px. Cuerpo con interlineado 1.6, títulos 1.2. Espaciado base 8 px.

## Paletas de los cuatro temas

| Tema | Fondo | Superficie | Texto | Texto secundario | Acción | Texto del botón |
|---|---|---|---|---|---|---|
| Claro | #FAF7F0 | #FFFDF9 | #38271E | #75675C | #65452F | #FFF9EF |
| Oscuro | #211B17 | #2C241E | #F7F0E6 | #C5B5A3 | #D7B28D | #211B17 |
| Vintage | #EEE2C9 | #F7EEDB | #493727 | #756046 | #745033 | #FFF5DF |
| Pastel | #FCF5F0 | #FFFDFB | #533D39 | #7C6560 | #795C60 | #FFFAF7 |

Claro: principal, crema y espresso. Oscuro: cacao y arena, cálido e íntimo.
Vintage: papel, café tostado y títulos de imprenta. Pastel: marfil y rosa té,
con bordes suaves. Caramelo #B68B65 para detalles, no para texto pequeño.
Mantener foco visible, etiquetas y jerarquía. El estado no debe depender solo del color.

## Diez wireframes y flujo

| Página | Ruta | Estructura y acción principal |
|---|---|---|
| Inicio | / | Encabezado, presentación, favoritos, beneficios, pie. Explorar cafés. |
| Catálogo | /catalogo | Título, búsqueda, filtros, grilla, resultados. Ver producto. |
| Detalle | /producto/:id | Imagen, nombre, precio, descripción, formato, cantidad. Agregar. |
| Carrito | /carrito | Productos, cantidades, eliminar, resumen y total. Continuar. |
| Login | /login | Correo, contraseña, validación, enlace a Registro. Entrar. |
| Registro | /registro | Nombre, correo, contraseña y confirmación, términos. Crear cuenta. |
| Pago | /pago | Progreso, contacto, entrega, medio de pago, resumen. Confirmar. |
| Confirmación | /confirmacion | Resultado, número, resumen, retiro y correo. Volver al catálogo. |
| Contacto | /contacto | Canales, ubicación, formulario y estados de envío. Enviar consulta. |
| Quiénes somos | /quienes-somos | Historia, imagen del equipo, valores. Descubrir cafés. |

Flujo principal: Inicio → Catálogo → Detalle → Carrito → Login/Registro → Pago
→ Confirmación. Registro vuelve a Login; Confirmación vuelve a Catálogo.
Contacto y Quiénes somos son accesibles desde la navegación y el pie.
En celular, las columnas se apilan y los controles mantienen etiquetas visibles.

Estados a implementar en desarrollo: carga, listas vacías, filtros sin resultados,
producto sin stock, carrito vacío, validación, credenciales incorrectas, registro
duplicado, error de pago y respuesta de contacto. Los wireframes señalan los
espacios para esos estados; no implementan autenticación ni cobros.

## Alcance y conservación del Sprint 2

La copia de trabajo del Sprint 1 parte de `b5fd4f2`, anterior al panel administrativo.
El panel publicado está en el commit `b299ec7`; suspensión y reactivación permanecen
sin commit en la carpeta original `C:/Users/crist/OneDrive/Desktop/Solemne 2`.
No se ha retirado el panel de GitHub ni reescrito el historial en este trabajo.
La copia de Sprint 1 contiene solo propuestas de diseño dentro de `diseno/sprint-1`.
No crear commits ni publicar sin consultar al usuario.
