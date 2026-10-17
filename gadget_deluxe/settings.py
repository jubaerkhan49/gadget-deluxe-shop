"""
Django settings for gadget_deluxe project.
E-commerce website exclusively for used/refurbished iPhones:
iPhone 14 Pro, 14 Pro Max, 15 Pro, 15 Pro Max, 16 Pro, 16 Pro Max.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-czotav#58ni7$(mo%5a%#_2f_w@bntq0)t76bucxrdl*j=i59%'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip() 
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,gadgetdeluxe.shop,www.gadgetdeluxe.shop,.gadgetdeluxe.shop,.onrender.com').split(',') 
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 
        'https://gadgetdeluxe.shop,https://www.gadgetdeluxe.shop,https://*.onrender.com,http://localhost:8000,http://127.0.0.1:8000'
    ).split(',') 
    if origin.strip()
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    
    # Custom apps
    'store',
    'orders',
    'accounts',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dashboard.middleware.VisitorAnalyticsMiddleware',
]

ROOT_URLCONF = 'gadget_deluxe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart_context',
                'store.context_processors.store_settings_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'gadget_deluxe.wsgi.application'

# Database configuration (Neon PostgreSQL or fallback to SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require='neon.tech' in DATABASE_URL or 'render.com' in DATABASE_URL
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation (allow 6 digit/char passwords with no common password restrictions)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        },
    },
]


# Internationalization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('bn', 'বাংলা'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Product uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
os.makedirs(MEDIA_ROOT, exist_ok=True)

import cloudinary

# Cloudinary persistent media storage (keeps uploads safe across Render redeploys)
_raw_c_url = os.environ.get('CLOUDINARY_URL', '').strip()
_raw_c_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
_raw_c_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
_raw_c_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()

USE_CLOUDINARY = False

# Check if valid CLOUDINARY_URL provided (must have @ and not be a template placeholder like <API_KEY>)
if _raw_c_url and '@' in _raw_c_url and '<' not in _raw_c_url:
    try:
        cloudinary.reset_config()
        c_conf = cloudinary.config()
        if c_conf.cloud_name and '<' not in c_conf.cloud_name:
            USE_CLOUDINARY = True
            CLOUDINARY_STORAGE = {
                'CLOUD_NAME': c_conf.cloud_name,
                'API_KEY': c_conf.api_key,
                'API_SECRET': c_conf.api_secret,
            }
    except Exception:
        USE_CLOUDINARY = False
elif _raw_c_name and _raw_c_key and _raw_c_secret and '<' not in _raw_c_name:
    try:
        cloudinary.config(
            cloud_name=_raw_c_name,
            api_key=_raw_c_key,
            api_secret=_raw_c_secret,
            secure=True,
        )
        if cloudinary.config().cloud_name:
            USE_CLOUDINARY = True
            CLOUDINARY_STORAGE = {
                'CLOUD_NAME': _raw_c_name,
                'API_KEY': _raw_c_key,
                'API_SECRET': _raw_c_secret,
            }
    except Exception:
        USE_CLOUDINARY = False

if USE_CLOUDINARY:
    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

# Authentication redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'store:home'

# Email Configuration
if os.environ.get('EMAIL_HOST_USER') and os.environ.get('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Gadget Deluxe <gadgetdeluxe0@gmail.com>')

# Session / Cart
CART_SESSION_ID = 'gadget_deluxe_cart'
SESSION_COOKIE_AGE = 86400 * 30  # 30 days

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
