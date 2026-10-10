## En una terminal POWERSHELL (cmd no sirve), asegurense de estar en la ruta donde está el proyecto y dentro de la carpeta backend. Y ejecuten los siguentes comandos

1. python -m venv venv
2. .\venv\Scripts\activate.ps1

## ^ Con esto se activará el entorno virtual 

## Instalar dependencias:
pip install -r requerimientos.md

## Preparar la base de datos simulada:
python manage.py migrate

## Levantar el servidor:
python manage.py runserver

## Una vez levantado, entrar al siguiente link: "http://localhost:8000/api/test/", y si todo sale bien se deberia ver una pagina web.