"""
Django settings for core project (producción ligera en Windows + Cloudflare Tunnel).
"""
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv



# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env desde la raíz del proyecto, forzando override
ENV_FILE = find_dotenv(filename=".env", usecwd=True)
load_dotenv(ENV_FILE, override=True)



# ______________ Seguridad ______________
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-unsafe-key")


# DEBUG
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"



ALLOWED_HOSTS = [
    "ambugroupllc.work",
    "www.ambugroupllc.work",
    "localhost",
    "127.0.0.1"
]

# Detrás de Cloudflare (HTTPS)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies seguras (sirviendo por HTTPS a través de Cloudflare)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"

# Redirección a HTTPS
SECURE_SSL_REDIRECT = False

# HSTS (siempre HTTPS)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Orígenes de confianza para CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://ambugroupllc.work",
    "https://www.ambugroupllc.work",
]

# ───────────────── Apps ─────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "attendance",
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
APPEND_SLASH = True
# ───────────────── Middleware ─────────────────
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

# ───────────────── Templates ─────────────────
ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # si tienes carpeta templates global: [BASE_DIR / "templates"]
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Base de datos (desde .env)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGNAME", "ambu_app_db"),
        "USER": os.getenv("PGUSER", "postgres"),
        "PASSWORD": os.getenv("PGPASSWORD", "jorge2026."),
        "HOST": os.getenv("PGHOST", "host.docker.internal"),
        "PORT": os.getenv("PGPORT", "5432"),
    }
}

# ───────────────── Passwords ─────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────────────── i18n / zona horaria ─────────────────
LANGUAGE_CODE = "es"
TIME_ZONE = "America/New_York"  # Florida
USE_I18N = True
USE_TZ = True

# ───────────────── Static / Media ─────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

if (BASE_DIR / "static").exists():
    STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
