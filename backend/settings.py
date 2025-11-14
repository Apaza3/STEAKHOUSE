"""
Django settings for backend project.
...
"""

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-1u)i7v98&35^ynrg=hatf18=nhaq(q4-8%b=s_0+2^*kh&w)ei'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.0.95', '.onrender.com']

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


# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'es-bo' # Cambiado a español de Bolivia
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===================================================
# ¡CONFIGURACIÓN DE EMAIL CORREGIDA!
# ===================================================

# Para desarrollo (DEBUG=True), usamos la consola.
# ¡Esto imprimirá el email en tu terminal de `runserver`!
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- CONFIGURACIÓN DE GMAIL (PARA PRODUCCIÓN) ---
# (La dejamos aquí, pero Django la ignorará mientras DEBUG=True)
#
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'www.ajgamer4852h@gmail.com'
# EMAIL_HOST_PASSWORD = 'flcz kuof xgiu wqho' 
#
# NOTA: Para que esto funcione en Render, debes poner
# EMAIL_HOST_USER y EMAIL_HOST_PASSWORD como Variables de Entorno
# y NO dejarlas escritas aquí.
# ===================================================


# --- CONFIGURACIÓN DE ARCHIVOS MEDIA (Imágenes de Productos) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CONFIGURACIÓN PARA PRODUCCIÓN (Whitenoise) ---
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Le dice a Django dónde buscar archivos estáticos en desarrollo
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / "staticfiles_build"