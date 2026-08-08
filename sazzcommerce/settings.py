"""
Django settings for KenaKata — Bangladesh's Premium Marketplace & POS
"""
from pathlib import Path
import os
import secrets
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import sys

# Check if running automated tests or management checks
TESTING = 'test' in sys.argv or any('test' in arg for arg in sys.argv)
CHECKING = 'check' in sys.argv or any('check' in arg for arg in sys.argv)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG and not TESTING and not CHECKING:
        raise ImproperlyConfigured("SECRET_KEY environment variable is required in production.")
    # Safe ephemeral development/test/check key (never committed, >= 50 characters)
    SECRET_KEY = secrets.token_urlsafe(50)

# Configure ALLOWED_HOSTS safely
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

if 'RENDER' in os.environ:
    render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if render_host and render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_host)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # KenaKata apps
    'core',
    'accounts',
    'catalog',
    'cart',
    'wishlist',
    'orders',
    'reviews',
    'dashboard',
    'pos',
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

ROOT_URLCONF = 'sazzcommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_context',
                'wishlist.context_processors.wishlist_context',
                'catalog.context_processors.catalog_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sazzcommerce.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL / External Database via DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    except Exception as e:
        raise ImproperlyConfigured(f"DATABASE_URL was provided but failed to configure database: {e}")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if DEBUG else 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'kenakata_cache_table',
    }
}

# Production HTTPS / Security Headers
if not DEBUG and not TESTING:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_REDIRECT_URL = '/'

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 30  # 30 days

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# KenaKata Settings
BRAND_NAME = 'KenaKata'
BRAND_TAGLINE = 'Shop Smarter, Live Better — Delivered Across Bangladesh'
CURRENCY_SYMBOL = '৳'

# Delivery Configuration
DELIVERY_CHARGES = {
    'inside_dhaka': 60,
    'outside_dhaka': 120,
}

# Flash Sale (hours from now for demo)
FLASH_SALE_HOURS = 6

# Email (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

