import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# --- ¡CAMBIO IMPORTANTE! ---
# Lee la SECRET_KEY desde las variables de entorno de Render
SECRET_KEY = os.environ.get('SECRET_KEY')

# --- ¡CAMBIO IMPORTANTE! ---
# DEBUG se desactiva automáticamente en Render, pero se mantiene True localmente.
# 'RENDER' es una variable que Render añade automáticamente.
DEBUG = 'RENDER' not in os.environ

# --- ¡CAMBIO IMPORTANTE! ---
# ALLOWED_HOSTS lee la URL de tu sitio en Render.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_URL.split('//')[-1])


# Application definition
INSTALLED_APPS = [
    'core',
    'reservas',
    'ventas',
    'compras',
    'pedidos',
    'productos',
    'dashboard',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise (archivos estáticos) debe ir aquí
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# --- ¡CAMBIO IMPORTANTE! ---
# Configura la base de datos para leer la URL de Render (PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        # Lee la variable 'DATABASE_URL' de Render
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# --- ¡NUEVO! Seguridad para Render ---
# Le dice a Django que confíe en la URL de Render para formularios (CSRF)
if RENDER_EXTERNAL_URL:
    CSRF_TRUSTED_ORIGINS = [RENDER_EXTERNAL_URL]


# Password validation (sin cambios)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization (sin cambios)
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I1N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_build' # Directorio para collectstatic
STATICFILES_STORAGE = 'whitenoise.storage.WhiteNoiseStorage'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (Imágenes de Productos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===================================================
# ¡CAMBIO IMPORTANTE! Configuración de Email (Modo Producción)
# ===================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# --- Lee las credenciales de las variables de entorno ---
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# ===================================================