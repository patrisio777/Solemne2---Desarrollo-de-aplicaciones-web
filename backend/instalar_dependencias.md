## Guía de Instalación y Ejecución del Backend

En una terminal **PowerShell** (no CMD), asegúrate de estar en la raíz de la carpeta `backend`:

```powershell
cd backend
```

---

### 1. Crear y Activar Entorno Virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Deberás ver `(venv)` al inicio de tu línea de comandos).*

---

### 2. Configurar Variables de Entorno (`.env`)
Copia el archivo de ejemplo para generar tu configuración local:
```powershell
Copy-Item .env.example .env
```
* **PostgreSQL:** Cuando tengas tu base de datos lista en PostgreSQL, cambia `USE_POSTGRESQL=True` y coloca tu contraseña en el archivo `.env`. Mientras tanto, con `USE_POSTGRESQL=False` el sistema usará SQLite local de respaldo para que puedas trabajar sin bloqueos.
* **MongoDB Atlas:** Coloca tu string de conexión (`MONGODB_URI`) en `.env`.

---

### 3. Instalar Dependencias
Instala los paquetes necesarios (Django, DRF, PostgreSQL, MongoDB, CORS, Dotenv):
```powershell
pip install -r requerimientos.md
```

---

### 4. Preparar la Base de Datos (Migraciones)
Aplica las tablas de usuarios, catálogo, pedidos y transacciones:
```powershell
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Levantar el Servidor Backend
```powershell
python manage.py runserver
```

---

### 6. Endpoints de Verificación
Una vez iniciado el servidor, valida en tu navegador:
1. **Prueba de conexión básica:** [http://localhost:8000/api/test/](http://localhost:8000/api/test/)
2. **Estado de ambas Bases de Datos (PSQL y MongoDB):** [http://localhost:8000/api/db-status/](http://localhost:8000/api/db-status/)
3. **Panel Administrativo:** [http://localhost:8000/admin/](http://localhost:8000/admin/)