# 2. Investigación de Pasarela de Pago en Modo Sandbox

**Tarea Sprint 1** — *Investigar pasarela de pago Sandbox* [Javiera Fuentealba]
**Alcance:** solo investigación e integración planificada. Según el estado del
proyecto, la pasarela está *investigada*, no implementada: no existe aún código
de cobro en el backend.

---

## 1. Objetivo

Definir qué pasarela externa usará «Paraíso del Café» para cobrar en modo
**sandbox** (entorno de pruebas con dinero ficticio), cómo se integra con
Django + DRF y qué piezas del modelo actual (pedidos, stock, auditoría) quedan
involucradas antes de escribir la primera línea de integración.

## 2. Opciones evaluadas

| Criterio | **Transbank Webpay Plus** | Mercado Pago | Stripe Checkout |
|---|---|---|---|
| Cobertura de medio de pago en Chile | Tarjetas chilenas (débito/crédito), Webpay, Khipu | Internacional + algunos medios locales | Internacional |
| Entorno sandbox | Sí (entorno de integración con comercio de prueba) | Sí (cuenta de prueba) | Sí (modo test con claves de prueba) |
| Integración con backend | SDK oficial `transbank` (Python) y API REST | SDK/REST + webhooks | SDK/REST + webhooks |
| Retorno al sitio | URL de retorno configurable (sincrónico) | Webhooks (asincrónico) + redirección | Webhooks (asincrónico) + redirección |
| Costo de arranque | Requiere comercio aprobado para producción | Registro inmediato | Registro inmediato |
| Ajuste al proyecto | **Alto**: moneda CLP, público chileno, ya presente en `.env.example` | Medio | Medio |

**Decisión de investigación: Transbank Webpay Plus (sandbox).** Es la opción
natural para una cafetería chilena que opera en pesos, el `.env.example` ya
incluye su bloque de configuración (`TRANSBANK_ENVIRONMENT=INTEGRATION`,
`TRANSBANK_COMMERCE_CODE=597055555532`, `TRANSBANK_API_KEY=...` — credenciales
públicas de prueba de Transbank) y su flujo síncrono encaja con el flujo
Carrito → Pago → Confirmación del frontend.

## 3. Flujo de Webpay Plus (modo sandbox)

```
Frontend (React)          Backend (Django/DRF)              Transbank (sandbox)
      |                            |                                |
      | POST /api/pagos/iniciar    |                                |
      | (pedido + montos)          |                                |
      | -------------------------> | Crear sesión de pago            |
      |                            | (buyOrder, sessionId, monto,    |
      |                            |  returnUrl)                    |
      |                            | -----------------------------> |
      |                            | <---- token (URL de pago) ----- |
      | <--- url/token_ws --------- |                                |
      | redirige al navegador  ----------------------------------->  |
      |                            |                                |
      |     (usuario paga con tarjeta de prueba en la página de Transbank)
      | <--- returnUrl?token_ws=... --------------------------------- |
      | POST /api/pagos/confirmar  |                                |
      | -------------------------> | confirmar transacción (commit) |
      |                            | -----------------------------> |
      |                            | <---- estado final + montos --- |
      |                            | Actualiza Pedido + PagoTransaccion
      | <--- estado del pago ------ |                                |
      | muestra /confirmacion o /pago                                 |
```

Puntos clave verificados:

1. **Confirmación server-to-server.** El navegador vuelve con un `token_ws`;
   el backend debe confirmarlo contra Transbank **antes** de marcar el pedido
   como pagado. Nunca confiar solo en que el usuario llegó a `/confirmacion`.
2. **Idempotencia.** Confirmar dos veces el mismo `token_ws` debe responder lo
   mismo y **no** descontar stock dos veces. El `PagoTransaccion` ya modela
   `token_pasarela` como único (`unique=True`), lo que permite detectar
   reintentos.
3. **Estados.** El modelo existente `PagoTransaccion.ESTADOS_PAGO`
   (`INICIADO`, `AUTORIZADO`, `RECHAZADO`, `REVERSADO`) cubre el ciclo de vida
   sin cambios.
4. **Reservas de stock.** Al iniciar el pago conviene pasar unidades del
   `stock_fisico` al `stock_reservado` del producto y liberarlas si la
   transacción se rechaza o expira (RF pendiente del Sprint 4/5: «Stock
   reservado: se define en el esquema, pero no hay tarea que reserve o libere
   stock durante la compra»).
5. **Auditoría en MongoDB.** Toda respuesta cruda de la pasarela (webhooks,
   confirmaciones, errores) se registra con `registrar_log_pasarela()` en la
   colección `logs_pasarela_pagos` (ya implementada en
   `api/mongo_collections.py`).

## 4. Credenciales y configuración sandbox

El archivo `backend/.env.example` ya expone la configuración de prueba
(**credenciales públicas de integración**, no secretos de producción):

```dotenv
TRANSBANK_ENVIRONMENT=INTEGRATION
TRANSBANK_COMMERCE_CODE=597055555532
TRANSBANK_API_KEY=<clave pública de integración de Transbank>
TRANSBANK_RETURN_URL=http://localhost:8000/api/pagos/confirmar/
FRONTEND_CONFIRMATION_URL=http://localhost:5173/confirmacion
FRONTEND_REJECTED_URL=http://localhost:5173/pago
```

- Las **tarjetas de prueba** (montos que fuerzan aprobación, rechazo, etc.)
  están publicadas en la documentación oficial de Transbank para el entorno de
  integración; no se incrustan en el repositorio para no quedar desactualizadas.
- En producción estas variables se reemplazan por credenciales reales en el
  `.env` (nunca versionado) y el entorno pasa de `INTEGRATION` a `PRODUCTION`.

## 5. Plan de integración en Django + DRF (pendiente)

| Paso | Endpoint propuesto | Descripción |
|---|---|---|
| 1 | `POST /api/pagos/iniciar` | Valida el carrito, crea/reserva el `Pedido` y solicita la sesión de pago a Transbank; devuelve la URL de pago. |
| 2 | `POST /api/pagos/confirmar` | Recibe `token_ws` desde la URL de retorno, ejecuta el commit contra Transbank, actualiza `PagoTransaccion` y libera o descuenta stock de forma idempotente. |
| 3 | Webhook (opcional) | Notificación asincrónica de Transbank con verificación de origen; misma lógica de idempotencia que el paso 2. |
| 4 | `GET /api/pagos/<pedido_id>/` | Estado del pago para pintar la página de Confirmación. |

Requisitos transversales: todo el flujo protegido con token de administrador o
sesión de cliente, errores sin revelar datos internos y registro completo en
`logs_pasarela_pagos`.

## 6. Limitaciones conocidas

- El flujo completo **aún no está implementado** (figura en el roadmap del
  README como mejora posterior a esta investigación).
- El frontend de Carrito / Pago / Confirmación sigue siendo la página base del
  Sprint 1: no lógica de compra todavía.
- No hay gestión de pedidos (creación, estados, historial) más allá de los
  modelos relacionales `Pedido` / `DetallePedido` / `PagoTransaccion`.
- La verificación de webhooks y la liberación automática de reservas quedan
  pendientes hasta implementar los endpoints de la sección 5.
