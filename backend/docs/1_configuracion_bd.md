# Configuración Inicial de Bases de Datos

---

## 1. Resumen Ejecutivo
Para el desarrollo de la plataforma web de la cafetería se implementó una **arquitectura de persistencia políglota (Polyglot Persistence)**, combinando dos tipos de motores de bases de datos para optimizar el rendimiento y la integridad de los datos:
1. **Base de Datos Relacional (PostgreSQL):** Utilizada como la base de datos principal para la gestión transaccional, órdenes de compra, control de inventario de productos, pagos y autenticación de usuarios bajo estándares ACID.
2. **Base de Datos No Relacional (MongoDB Atlas):** Utilizada como clúster en la nube para el almacenamiento de datos semiestructurados, logs de auditoría de pasarelas de pago externas (payloads JSON de transacciones), mensajes de contacto y atributos dinámicos de los granos de café.

---

## 2. Configuración del Entorno Relacional (PostgreSQL)

### A. Opciones de Instalación
* **Opción Local (Recomendada para desarrollo):**
  1. Descargar e instalar PostgreSQL para Windows desde [postgresql.org](https://www.postgresql.org/download/windows/).
  2. Mantener el puerto predeterminado `5432`.
  3. Abrir **pgAdmin 4** o la terminal **SQL Shell (psql)**.
* **Opción Nube (Supabase / Render / Neon):**
  1. Crear un proyecto gratuito en Supabase o Render PostgreSQL.
  2. Obtener el Host, Nombre de Base de Datos, Usuario, Contraseña y Puerto proporcionados.

### B. Creación de la Base de Datos
Ejecutar la siguiente sentencia SQL en pgAdmin o en la consola `psql`:

```sql
-- 1. Crear la base de datos del proyecto
CREATE DATABASE paraiso_cafe_db;

-- 2. (Opcional) Crear un usuario específico si no se desea usar 'postgres'
CREATE USER cafe_admin WITH PASSWORD 'clave_segura_123';
GRANT ALL PRIVILEGES ON DATABASE paraiso_cafe_db TO cafe_admin;
```

### C. Conexión en Django (`backend/.env`)
En el archivo `backend/.env`, configurar las siguientes variables:

```env
USE_POSTGRESQL=True
DB_NAME=paraiso_cafe_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_de_postgresql
DB_HOST=localhost
DB_PORT=5432
```

> **Nota de Respaldo:** Si `USE_POSTGRESQL=False`, el sistema automáticamente utilizará `SQLite` local (`db.sqlite3`), permitiendo que cualquier integrante del equipo continúe trabajando sin interrupciones mientras instala PostgreSQL.

---

## 3. Configuración del Entorno No Relacional (MongoDB Atlas)

### A. Creación de Clúster Gratuito en la Nube
1. Ingresar a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) e iniciar sesión o registrarse.
2. Crear un nuevo proyecto llamado `ParaisoDelCafe`.
3. Seleccionar **Deploy a Database** y elegir el plan **M0 Free (Shared)**.
4. Seleccionar un proveedor (AWS / Google Cloud) y la región más cercana (ej: `sa-east-1` São Paulo).
5. Asignar el nombre del clúster (por ejemplo `Cluster0` o `ClusterCafe`) y hacer clic en **Create Deployment**.

### B. Configuración de Seguridad
* **Database Access (Usuario de BD):**
  1. Ir a **Security** > **Database Access**.
  2. Hacer clic en **Add New Database User**.
  3. Método de autenticación: `Password`.
  4. Usuario: `admin_cafe`
  5. Contraseña: Generar o escribir una contraseña segura (anotarla, ej: `CafeClave2026`).
  6. Privilegios: `Read and write to any database`.
* **Network Access (IP Whitelist):**
  1. Ir a **Security** > **Network Access**.
  2. Hacer clic en **Add IP Address**.
  3. Seleccionar **Allow Access from Anywhere** (`0.0.0.0/0`) para permitir el acceso durante la fase de desarrollo y pruebas.
  4. Confirmar los cambios.

### C. Obtención de la Cadena de Conexión (Connection String)
1. En la pestaña **Overview** del Clúster, presionar **Connect**.
2. Seleccionar la opción **Drivers** (Python).
3. Seleccionar la versión `3.12 or later`.
4. Copiar el string de conexión URI que tiene el siguiente formato:
   ```
   mongodb+srv://admin_cafe:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Reemplazar `<password>` por la contraseña creada para el usuario.

### D. Configuración en Django (`backend/.env`)
En el archivo `backend/.env`:

```env
MONGODB_URI=mongodb+srv://admin_cafe:tu_clave@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=paraiso_cafe_nosql
```

---

## 4. Dependencias del Proyecto
Las dependencias requeridas para soportar ambos entornos se encuentran en `backend/requerimientos.md` y `backend/requirements.txt`:

```text
Django==6.1.1
djangorestframework==3.18.1
psycopg2-binary>=2.9.9
pymongo>=4.6.0
python-dotenv>=1.0.0
django-cors-headers>=4.3.0
```

Para instalarlas dentro del entorno virtual:
```powershell
pip install -r requerimientos.md
```

---

## 5. Aplicar Migraciones y Validar Conexiones

### A. Ejecutar migraciones en PostgreSQL
Con el entorno virtual activo y PostgreSQL encendido:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### B. Endpoint de Verificación Automatizada (`/api/db-status/`)
El proyecto incluye un endpoint especializado para validar en tiempo real el estado de ambos entornos.

1. Iniciar el servidor backend:
   ```powershell
   python manage.py runserver
   ```
2. Acceder en el navegador a: `http://localhost:8000/api/db-status/`
3. La respuesta entregará el diagnóstico detallado:
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
         "message": "Conexión exitosa a PostgreSQL"
       },
       "no_relacional_mongodb": {
         "connected": true,
         "status": "connected",
         "database": "paraiso_cafe_nosql",
         "message": "Conexión exitosa con MongoDB Atlas"
       }
     }
   }
   ```
