# ============================================================
# ⚙️ CONFIGURACIÓN DJANGO - Sistema de Nómina IS2
# ============================================================
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import smtplib

# ------------------------------------------------------------
# 🔹 RUTAS BASE Y VARIABLES DE ENTORNO
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# 👇 Cargar archivo .env desde la raíz del backend
# (asegurate de que exista C:\Users\Ojeda\Is2-payroll-app\backend\.env)
load_dotenv(BASE_DIR / ".env")

# ------------------------------------------------------------
# 🔹 CONFIGURACIÓN GENERAL DEL PROYECTO
# ------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-1234567890")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ------------------------------------------------------------
# 🔹 APLICACIONES INSTALADAS
# ------------------------------------------------------------
INSTALLED_APPS = [
    # Núcleo de Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Librerías de terceros
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",

    # Aplicaciones del sistema
    "usuarios",
    "empleados",
    "asistencia",
    "nomina_cal.apps.NominaCalConfig",
    "auditoria.apps.AuditoriaConfig",
]

# ------------------------------------------------------------
# 🔹 MIDDLEWARE
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS primero para habilitar orígenes del frontend
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Auditoría (tu middleware)
    "auditoria.middleware.AuditlogMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------
# 🔹 CONFIGURACIÓN DE URLS Y WSGI
# ------------------------------------------------------------
ROOT_URLCONF = "sistema_nomina.urls"
WSGI_APPLICATION = "sistema_nomina.wsgi.application"

# ------------------------------------------------------------
# 🔹 CONFIGURACIÓN DE PLANTILLAS
# ------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # 📁 Plantillas HTML y correos
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------
# 🔹 BASE DE DATOS (PostgreSQL)
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "nomina_db"),
        "USER": os.getenv("DB_USER", "is2"),
        "PASSWORD": os.getenv("DB_PASSWORD", "teamis2"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# ------------------------------------------------------------
# 🔹 AUTENTICACIÓN Y PERMISOS
# ------------------------------------------------------------
AUTH_USER_MODEL = "usuarios.Usuario"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    # Opcional: paginación tipo admin (50 por página)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

# ------------------------------------------------------------
# 🔹 CONFIGURACIÓN JWT (Tokens de sesión)
# ------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ------------------------------------------------------------
# 🔹 CONFIGURACIÓN CORS / CSRF (Frontend con Vite)
# ------------------------------------------------------------
# Permitimos http://localhost:5173 y http://127.0.0.1:5173
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
_frontend_host = _frontend_url

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = list({
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    _frontend_host,
})
CORS_ALLOW_CREDENTIALS = True

# CSRF confiable para el frontend
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    _frontend_host,
]

# ------------------------------------------------------------
# 🔹 VALIDADORES DE CONTRASEÑA
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------
# 🔹 INTERNACIONALIZACIÓN Y ZONA HORARIA
# ------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Asuncion"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# 🔹 ARCHIVOS ESTÁTICOS Y MEDIA
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------
# 🔹 DEFAULT AUTO FIELD
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------
# 🔹 LOGGING
# ------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# ============================================================
# 💌 CONFIGURACIÓN DE CORREO ELECTRÓNICO (EMAIL BACKEND)
# Sistema de Nómina IS2 — FP-UNA / FAP
# ------------------------------------------------------------
# Modos soportados (definí EMAIL_MODE en tu .env):
#   console  → imprime correos en terminal (desarrollo)
#   gmail    → Gmail SMTP (recomendado, por defecto)
#   outlook  → Outlook / Office365
#   smtp     → SMTP institucional
#   sendgrid → SendGrid SMTP con API Key
# ============================================================

# 🌍 URL base del frontend (para enlaces de reseteo de contraseña)
FRONTEND_URL = _frontend_url

EMAIL_MODE = os.getenv("EMAIL_MODE", "gmail").lower()

if EMAIL_MODE == "console":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@nomina.local")

elif EMAIL_MODE == "gmail":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "ojeda.cardozo90@gmail.com")
    # Requiere "App Password" (2FA): https://myaccount.google.com/apppasswords
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

elif EMAIL_MODE == "outlook":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.office365.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "tuusuario@outlook.com")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

elif EMAIL_MODE == "smtp":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "mail.fap.mil.py")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "tuusuario@fap.mil.py")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

elif EMAIL_MODE == "sendgrid":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = "apikey"
    EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_API_KEY", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "notificaciones@nomina.com")

else:
    # Fallback seguro: consola (no intenta enviar)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@nomina.local")

# Nivel de depuración SMTP (0=off, 1=verbose)
SMTP_DEBUG = int(os.getenv("SMTP_DEBUG", "0"))
smtplib.SMTP.debuglevel = SMTP_DEBUG
