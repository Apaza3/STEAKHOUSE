#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala las librerías
pip install -r requirements.txt

# Recolecta los archivos estáticos (CSS, imágenes) para que Whitenoise los sirva
python manage.py collectstatic --no-input

# Ejecuta las migraciones para actualizar la base de datos en la nube
python manage.py migrate

#crea un usuario admin si no existe
python manage.py create_admin