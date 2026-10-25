# Paraíso del Café — Solemne 2: Desarrollo de Aplicaciones Web

> **«Un sorbo al paraíso»**  
> Plataforma web integral de comercio electrónico y gestión para cafetería de especialidad, desarrollada con una arquitectura desacoplada y persistencia políglota (PostgreSQL + MongoDB Atlas).

---

## 1. Equipo, Scrum Master y Responsabilidades

| Integrante | Rol / Responsabilidad | Área Principal | Tareas Asignadas |
|---|---|---|---|
| **Patricio Chaug** | **Scrum Master (SM)** & Desarrollador Frontend | Gestión Ágil & Frontend | Coordinación de ceremonias ágiles, organización de sprints, tablero de tareas, desarrollo de componentes e interfaz en React + Vite. |
| **Javiera Fuentealba** | Desarrolladora Backend | Backend & Bases de Datos | Configuración del entorno Django, endpoints de autenticación por Token, conexión y modelos en PostgreSQL y MongoDB Atlas, e investigación de pasarela de pago en modo Sandbox. |
| **Brandon Valdés** | Desarrollador Backend | Backend & API REST | Desarrollo de endpoints RESTful, validación de datos, control de lógica de negocio y gestión de usuarios. |
| **Gabriel Moreno** | Desarrollador Backend | Backend & Seguridad | Implementación de validaciones de seguridad, endpoints de salud/diagnóstico de BD, manejo de estados y sesiones. |
| **Cristóbal Garrido** | Diseñador UI/UX & Desarrollador Frontend | Diseño & Frontend | Identidad corporativa, wireframes y bocetos navegables (Sprint 1), diseño de paletas temáticas y maquetación de vistas en React. |
| **José Argüello** | Desarrollador Frontend | Frontend & Integración | Implementación de vistas navegables, enrutamiento con React Router DOM, integración de componentes y consumo de la API. |

---

## 2. Contexto, Alcance y Mejoras Opcionales

### 2.1 Contexto del Negocio
**Paraíso del Café** es una tienda de café de especialidad y salón artesanal que busca digitalizar la experiencia de compra de sus clientes. La solución aborda tanto la visualización interactiva del catálogo y formatos de molienda como la gestión de pedidos, registro seguro de clientes y auditoría de transacciones.

### 2.2 Alcance del Proyecto
* **Sprint 1 (Diseño e Identidad):**
  * Definición de identidad de marca (isotipo y logotipo vectorial en SVG).
  * 4 paletas temáticas accesibles: Claro, Oscuro, Vintage y Pastel.
  * Wireframes interactivos y responsivos de 10 vistas clave (Inicio, Catálogo, Detalle, Carrito, Login, Registro, Pago, Confirmación, Contacto, Quiénes Somos).
* **Sprint 2 (Arquitectura, Backend y Base de Datos):**
  * Configuración de Backend desacoplado con **Django REST Framework (DRF)**.
  * **Persistencia Políglota**: Integración de PostgreSQL (transaccional relacional) y MongoDB Atlas (datos flexibles NoSQL).
  * Mecanismo de fallback a SQLite para desarrollo ágil sin bloqueos locales.
  * Endpoints de salud y verificación de estado en tiempo real (`/api/db-status/` y `/api/health/`).
  * Autenticación segura mediante Tokens (`/api/registro/`, `/api/login/`, `/api/logout/`) con soporte de suspensión de cuentas (`is_active`).
  * Gestión de usuarios (`/api/users/`, `/api/users/<id>/`).
  * Interfaz Frontend moderna con **React 19** y **Vite**.
  * **Investigación Técnica de Pasarela de Pagos Sandbox** ([backend/docs/2_investigacion_pasarela_pago_sandbox.md](backend/docs/2_investigacion_pasarela_pago_sandbox.md)).

### 2.3 Mejoras Opcionales (Roadmap Futuro)
- [x] **Investigación de pasarela de pago en modo Sandbox:** Análisis de Transbank Webpay Plus, Mercado Pago y Stripe con guía de integración Django + DRF ([Documento Técnico](backend/docs/2_investigacion_pasarela_pago_sandbox.md)).
- [ ] Integración con pasarela de pago real (Webpay Plus / Stripe) mediante webhooks con verificación criptográfica e idempotencia.
- [ ] Sistema de reservas de mesas y programación de retiro en tienda física.
- [ ] Envío automático de boletas electrónicas y confirmación de pedidos vía correo (SMTP transaccional).
- [ ] Panel analítico para administradores con gráficos de ventas, productos favoritos y rotación de stock.
- [ ] Modo sin conexión (PWA) con caché local de catálogo para dispositivos móviles.

---

## 3. Arquitectura, Diagramas, Servicios y Datos

El sistema implementa una **arquitectura desacoplada (Decoupled Client-Server)** basada en servicios REST y persistencia políglota:

```mermaid
graph TD
    subgraph Cliente ["Capa de Presentación (Frontend)"]
        UI["React 19 + Vite SPA<br>(Puerto 5173)"]
        Design["Bocetos Sprint 1<br>(HTML/CSS Puro - Puerto 5175)"]
    end

    subgraph Servidor ["Capa de Lógica de Negocio (Backend)"]
        API["Django REST Framework API<br>(Puerto 8000)"]
        Auth["Servicio de Autenticación<br>(Tokens / Passwords Hashed)"]
        Health["Monitor de Salud & DB Status<br>(/api/db-status/)"]
    end

    subgraph Persistencia ["Capa de Persistencia Políglota"]
        Postgres[("PostgreSQL 15+<br>Datos Transaccionales, Usuarios,<br>Roles, Pedidos (ACID)")]
        Mongo[("MongoDB Atlas NoSQL<br>Auditoría de Pagos, Mensajes Contacto,<br>Atributos Dinámicos")]
        SQLite[("SQLite (db.sqlite3)<br>Fallback local de desarrollo")]
    end

    UI -->|Peticiones HTTP / JSON + Bearer Token| API
    API --> Auth
    API --> Health
    API -->|USE_POSTGRESQL=True| Postgres
    API -.->|USE_POSTGRESQL=False (Fallback)| SQLite
    API -->|PyMongo Driver| Mongo
```

### 3.1 Modelo de Datos y Distribución
* **Base de Datos Relacional (PostgreSQL / SQLite Fallback):**
  * `auth_user`: Credenciales, correo único, estado activo/suspendido (`is_active`), roles y permisos (`is_staff`).
  * `authtoken_token`: Tokens de sesión para autenticación en la API REST de Django.
  * `Categoria` (`api_categoria`): Clasificación del catálogo (Grano, Molido, Repostería, Accesorios).
  * `Producto` (`api_producto`): Catálogo comercial con precio en CLP, unidades en inventario (`stock`) y formato.
  * `Pedido` (`api_pedido`) y `DetallePedido` (`api_detallepedido`): Gestión transaccional de compras con aislamiento ACID e integridad referencial protegida (`PROTECT`).
  * `PagoTransaccion` (`api_pagotransaccion`): Registro formal de transacciones bancarias, montos y códigos de aprobación.
* **Base de Datos No Relacional (MongoDB Atlas):**
  * Colección `mensajes_contacto`: Consultas y mensajes recibidos desde el formulario de contacto web.
  * Colección `logs_pasarela_pagos`: Payloads JSON en bruto y trazas forenses de pasarelas de pago (Transbank Webpay / Stripe).
  * Colección `fichas_tecnicas_cafe`: Metadatos botánicos y sensoriales variables (notas de cata, altitud m.s.n.m., proceso, curvas de tueste).
  * Colección `resenas_productos`: Opiniones, valoraciones de 1 a 5 estrellas y feedback flexible de clientes.

---

## 4. Versiones, Compatibilidad, Prerrequisitos y Cuentas

### 4.1 Tecnologías y Versiones Obligatorias
* **Python:** `v3.10` a `v3.12+`
* **Django:** `6.1.1`
* **Django REST Framework:** `3.18.1`
* **Node.js:** `v18.x` o `v20.x` (LTS recomendado)
* **npm:** `v9.x` o superior
* **PostgreSQL:** `v14` a `v16+` (predeterminado en puerto `5432`)
* **React:** `19.2.x`
* **Vite:** `8.3.x`

### 4.2 Cuentas y Accesos Externos
1. **Cuenta en MongoDB Atlas:** Gratuita (Tier M0) para clúster en la nube.
2. **PostgreSQL Local o en Nube:** Servidor PostgreSQL local instalado o proveedor remoto (Supabase / Render / Neon).
3. **Cuenta GitHub:** Para clonar y contribuir al repositorio.

---

## 5. Instalación desde Clon Limpio y Comandos por Servicio

### 5.1 Clonar el Repositorio (Backend)
```bash
git clone https://github.com/ReneGG/dwebs03BackendCafein-manos.git
cd dwebs03BackendCafein-manos
```

---

### 5.2 Configuración del Backend (Django REST Framework)

1. **Ingresar al directorio del backend:**
   ```powershell
   cd dwebs03BackendCafein-manos
   # (Si el proyecto se ejecuta desde una subcarpeta backend, ejecutar: cd backend)
   ```

2. **Crear y activar entorno virtual:**
   * En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * En Linux / macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias de Python:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurar el archivo de entorno `.env`:**
   ```powershell
   Copy-Item .env.example .env
   # En Linux/macOS: cp .env.example .env
   ```
   *(Edita el archivo `.env` según tus credenciales de PostgreSQL y MongoDB Atlas; ver [Sección 6](#6-variables-de-entorno-sin-valores-secretos)).*

5. **Ejecutar migraciones de la base de datos:**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Iniciar el servidor de desarrollo:**
   ```powershell
   python manage.py runserver
   ```
   *El servidor quedará disponible en:* `http://localhost:8000/`

---

### 5.3 Configuración del Frontend (React + Vite)

1. **Abrir una nueva terminal y navegar a la carpeta `frontend`:**
   ```bash
   cd frontend
   ```

2. **Instalar dependencias de Node.js:**
   ```bash
   npm install
   ```

3. **Ejecutar el servidor de desarrollo:**
   ```bash
   npm run dev
   ```
   *La aplicación web estará disponible en:* `http://localhost:5173/`

4. **Comandos disponibles para Frontend:**
   | Comando | Acción |
   |---|---|
   | `npm run dev` | Inicia el servidor de desarrollo con recarga en vivo (HMR). |
   | `npm run build` | Genera los binarios optimizados de producción en la carpeta `dist/`. |
   | `npm run preview` | Previsualiza localmente la compilación de producción. |
   | `npm run lint` | Ejecuta ESLint para analizar la calidad del código. |

---

### 5.4 Previsualización de Bocetos y Diseño (Sprint 1)

Los bocetos de diseño estático no requieren instalación de dependencias de Node:
```powershell
cd diseno/sprint-1
python -m http.server 5175 --bind 127.0.0.1
```
*Abrir en el navegador:* `http://localhost:5175/index.html`

---

## 6. Variables de Entorno (Sin Valores Secretos)

El archivo `.env` reside en la raíz del proyecto backend (`dwebs03BackendCafein-manos/` o subcarpeta `backend/`) y **NUNCA** debe ser commiteado al repositorio. Utilice la siguiente plantilla (`.env.example`):

```env
# ==============================================================================
# CONFIGURACIÓN GENERAL DE DJANGO
# ==============================================================================
# Generar una clave secreta aleatoria en producción
DJANGO_SECRET_KEY=clave_secreta_de_ejemplo_cambiar_en_produccion_abcdef123456
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# ==============================================================================
# 1. BASE DE DATOS RELACIONAL: PostgreSQL (PSQL)
# ==============================================================================
# Cambiar a True para usar PostgreSQL. Si es False, usará SQLite local de respaldo.
USE_POSTGRESQL=True
DB_NAME=paraiso_cafe_db
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
DB_HOST=localhost
DB_PORT=5432

# ==============================================================================
# 2. BASE DE DATOS NO RELACIONAL: MongoDB Atlas
# ==============================================================================
# Cadena de conexión obtenida en Atlas: Connect -> Drivers -> Python
MONGODB_URI=mongodb+srv://<usuario>:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=paraiso_cafe_nosql

# ==============================================================================
# 3. POLÍTICA DE ORÍGENES CRUZADOS (CORS)
# ==============================================================================
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000
```

>Nunca comparta contraseñas ni cadenas URI de MongoDB en repositorios públicos. El archivo `.env` se encuentra explícitamente excluido mediante el `.gitignore`.

---

## 7. Datos Iniciales y Primer Administrador Seguro

### 7.1 Crear el Superusuario de Django
Para acceder al panel administrativo y gestionar usuarios o datos, ejecute de forma interactiva en la carpeta del backend (`dwebs03BackendCafein-manos`):

```powershell
python manage.py createsuperuser
```

* **Nombre de usuario / Correo:** `admin@paraisocafe.cl`
* **Contraseña segura:** Usar contraseñas que cumplan con la política de Django (mínimo 8 caracteres, alfanumérico, sin coincidencias con atributos personales).

### 7.2 Acceso al Panel Administrativo
Una vez iniciado el servidor backend, ingrese a:
* **URL:** `http://localhost:8000/admin/`
* Ingrese las credenciales creadas anteriormente.

### 7.3 Registro de Usuarios Clientes desde la API
Los usuarios estándar pueden registrarse mediante el endpoint seguro de la API:
* **POST** `/api/registro/`
* **Cuerpo JSON:**
  ```json
  {
    "email": "cliente@correo.cl",
    "password": "PasswordFuerte2026!",
    "nombre": "Ana",
    "apellido": "González"
  }
  ```
* El sistema encripta la clave mediante el algoritmo PBKDF2 con SHA-256 (estándar de Django) y retorna un Token de autenticación de respuesta inmediata.

---

## 8. Pruebas, Reportes, Estados, Reservas e Idempotencia

### 8.1 Ejecución de Pruebas Automatizadas
* **Backend:**
  ```powershell
  python manage.py test api
  ```
* **Frontend (Linting de sintaxis y buenas prácticas):**
  ```bash
  npm run lint
  ```

### 8.2 Endpoint de Diagnóstico y Salud (`/api/db-status/`)
Permite comprobar el estado de ambas bases de datos sin requerir inicio de sesión previo:
* **GET** `http://localhost:8000/api/db-status/`
* **Respuesta Exitosa Esperada:**
  ```json
  {
    "status": "ok",
    "timestamp": "America/Santiago",
    "bases_de_datos": {
      "relacional_psql": {
        "engine": "django.db.backends.postgresql",
        "name": "paraiso_cafe_db",
        "is_postgresql": true,
        "connected": true,
        "message": "conexion exitosa a postgresql"
      },
      "no_relacional_mongodb": {
        "connected": true,
        "status": "connected",
        "database": "paraiso_cafe_nosql",
        "message": "conexion exitosa con mongodb atlas"
      }
    }
  }
  ```

### 8.3 Códigos de Estado HTTP y Manejo de Errores
| Código HTTP | Descripción | Caso de Uso en la API |
|---|---|---|
| `200 OK` | Operación exitosa | Login completado, listado de usuarios, verificación de salud. |
| `201 CREATED` | Recurso creado | Registro exitoso de nuevo cliente. |
| `400 BAD REQUEST` | Datos inválidos | Email con formato incorrecto, contraseña débil o correo ya registrado. |
| `401 UNAUTHORIZED` | No autenticado | Credenciales incorrectas o token ausente/inválido. |
| `403 FORBIDDEN` | Acceso denegado | Intento de login en cuenta con `is_active: false` (cuenta suspendida). |
| `404 NOT FOUND` | No encontrado | Usuario u objeto inexistente para edición o consulta. |

### 8.4 Idempotencia y Concurrencia
* **Registro de Usuarios:** Idempotente frente a reintentos; si el correo ya existe, retorna `400 Bad Request` indicando que el registro ya fue procesado, impidiendo duplicidad de cuentas.
* **Actualización Parcial (`PATCH /api/users/<id>/`):** Las modificaciones aplican solo a los campos provistos, manteniendo la consistencia de los datos ante ejecuciones múltiples repetidas.
* **Diseño para Pagos y Reservas:** En la arquitectura de pagos (Sprint 2/3), se emplea un identificador único de transacción (`idempotency_key` o `order_id`) para evitar cobros duplicados en caso de reintentos por caída de red.

---

## 9. URLs, Plataformas, Cuotas y Persistencia

### 9.1 Tabla de URLs del Proyecto
| Servicio / Módulo | URL Local | Descripción |
|---|---|---|
| **Frontend Web** | `http://localhost:5173/` | Aplicación SPA principal en React. |
| **API Backend** | `http://localhost:8000/api/` | Raíz de servicios RESTful. |
| **Test Endpoint** | `http://localhost:8000/api/test/` | Comprobación rápida de respuesta backend. |
| **Diagnóstico DB** | `http://localhost:8000/api/db-status/` | Chequeo de conexión PostgreSQL y MongoDB. |
| **Panel Admin** | `http://localhost:8000/admin/` | Panel de gestión administrativa de Django. |
| **Bocetos Sprint 1** | `http://localhost:5175/` | Presentación estática de temas e identidad. |

### 9.2 Plataformas de Despliegue Sugeridas
* **Frontend:** Vercel o Netlify (despliegue continuo desde rama `main`).
* **Backend:** Render o Railway (entorno Linux con Gunicorn / Uvicorn).
* **Bases de Datos:**
  * **PostgreSQL:** Neon / Supabase / Render PostgreSQL.
  * **MongoDB:** MongoDB Atlas (AWS sa-east-1 São Paulo).

### 9.3 Cuotas y Restricciones (Free Tier)
* **MongoDB Atlas (M0 Shared):** Almacenamiento máximo de 512 MB, hasta 500 conexiones simultáneas. Tiempo de espera de conexión configurado a `serverSelectionTimeoutMS=4000` para evitar bloqueos si la red presenta latencia.
* **PostgreSQL (Local / Cloud Free):** Límite típico de conexiones concurrentes (20 a 100 conexiones).

---

## 10. Logs, Reintentos, Respaldos y Recuperación

### 10.1 Gestión de Logs y Diagnóstico
* Los errores de conexión de la base de datos se registran en la consola del servidor backend detallando la excepción.
* Monitoreo de latencia y estado a través del endpoint `/api/db-status/`.

### 10.2 Resiliencia y Fallback Automático
* **Mecanismo de Respaldo Local:** Si el servidor PostgreSQL del desarrollador no está activo o se trabaja sin conexión, basta con configurar `USE_POSTGRESQL=False` en el `.env` para que el sistema opere inmediatamente sobre `SQLite` (`db.sqlite3`).
* **Timeout en MongoDB:** Cliente singleton configurado con tiempo máximo de espera de 4 segundos para evitar que la aplicación quede bloqueada ante caídas del clúster remoto.

### 10.3 Políticas de Respaldos (Backup) y Restauración (Restore)

#### Respaldo de PostgreSQL:
```bash
# Exportar dump de la base de datos:
pg_dump -U postgres -h localhost paraiso_cafe_db > respaldo_paraiso_cafe.sql

# Restaurar en caso de contingencia:
psql -U postgres -h localhost -d paraiso_cafe_db < respaldo_paraiso_cafe.sql
```

#### Respaldo de MongoDB Atlas:
```bash
# Exportar colecciones con mongodump:
mongodump --uri="<TU_MONGODB_URI>" --out=./backup_mongo/

# Restaurar datos:
mongorestore --uri="<TU_MONGODB_URI>" ./backup_mongo/
```

---

## 11. Trazabilidad, Contribuciones y Limitaciones Conocidas

### 11.1 Flujo de Trabajo Git (Git Flow)
* `main`: Código estable probado y listo para entrega.
* `develop`: Integración de características del sprint en curso.
* `feature/<nombre>`: Ramas específicas para el desarrollo de módulos o endpoints.
* **Convención de Commits (Conventional Commits):**
  * `feat: ...` Nueva funcionalidad.
  * `fix: ...` Corrección de errores.
  * `docs: ...` Modificaciones en documentación o comentarios.
  * `style: ...` Ajustes visuales, CSS o formateo sin cambios en lógica.
  * `refactor: ...` Reestructuración de código sin alterar su comportamiento externo.

### 11.2 Limitaciones Conocidas
1. **Pasarela de Pagos:** En el Sprint actual la pasarela de pagos se encuentra en modalidad mock (wireframe navegable y validación de formulario, sin cargo bancario real en línea).
2. **Cuentas Suspendidas:** La suspensión de cuentas opera a nivel de backend validando `is_active=False` al momento de iniciar sesión y en la modificación mediante el endpoint `PATCH /api/users/<id>/`.

---

## 12. Procedencia y Licencias de Recursos

* **Recursos Gráficos y Multimedia:**
  * Logotipo e Isotipo (`logotipo.svg`, `simbolo.svg`): Creación original del equipo de diseño del proyecto bajo autoría de Cristóbal Garrido.
* **Tipografías:**
  * `Georgia` (Web-safe Serif) y `Trebuchet MS` (Web-safe Sans-Serif).
* **Licencias de Software:**
  * **Django:** Licencia BSD de 3 cláusulas.
  * **Django REST Framework:** Licencia Encode OSS.
  * **React & Vite:** Licencia MIT.
  * **PyMongo & Psycopg2:** Licencia Apache 2.0 / LGPL con excepciones.
* **Licencia del Repositorio:**
  * Proyecto académico bajo **Licencia MIT**. Consulte el repositorio para más detalles.
