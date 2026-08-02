import os

from dotenv import load_dotenv

from core.settings.get_env import getenv_bool, getenv_int, getenv_list

load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WSGI_APPLICATION = "core.wsgi.application"
AUTH_USER_MODEL = "profile_auth.User"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "corsheaders",
    "rest_framework.authtoken",

    "ps_schema",
    "django_filters",
    "profile_auth",
    "ocsa_legacy",
    "work_flux",
    "classify",
    "space_time",
    "project",
    "source",
    "actor",
    "impact",
    "event",
    "df",
    "task",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')
TEMPLATE_PATH = os.path.join(BASE_DIR, os.getenv("TEMPLATE_PATH", "templates"))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_PATH],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]


# -----------------------Default database configuration-----------------------
POSTRGRESQL_DB = os.getenv("POSTRGRESQL_DB", False)
DATABASE_NAME = os.getenv("DATABASE_NAME", "db.sqlite3")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
if POSTRGRESQL_DB:
    default_database = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DATABASE_NAME,
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": int(os.getenv("DATABASE_PORT", 5432)),
    }
else:
    default_database = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, DATABASE_NAME),
    }

if DATABASE_SCHEMA:
    default_database["OPTIONS"] = {  # type: ignore
        "options": f"-c search_path={DATABASE_SCHEMA}",
    }

DATABASES = {"default": default_database}
# ---------------------end Default database configuration---------------------


# -----------------------Legacy database configuration------------------------
DATABASE_LEGACY_NAME = os.getenv("DATABASE_LEGACY_NAME")
if DATABASE_LEGACY_NAME:
    POSTRGRESQL_LEGACY_DB = os.getenv("POSTRGRESQL_LEGACY_DB", False)
    DATABASE_LEGACY_SCHEMA = os.getenv("DATABASE_LEGACY_SCHEMA")
    if POSTRGRESQL_LEGACY_DB:
        legacy = {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": DATABASE_LEGACY_NAME,
            "USER": os.getenv("DATABASE_LEGACY_USER"),
            "PASSWORD": os.getenv("DATABASE_LEGACY_PASSWORD"),
            "HOST": os.getenv("DATABASE_LEGACY_HOST"),
            "PORT": int(os.getenv("DATABASE_LEGACY_PORT", 5432)),
        }
    else:
        legacy = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, DATABASE_LEGACY_NAME),
        }

    if DATABASE_LEGACY_SCHEMA:
        legacy["OPTIONS"] = {  # type: ignore
            "options": f"-c search_path={DATABASE_LEGACY_SCHEMA}",
        }

    DATABASES["legacy"] = legacy
    DATABASE_ROUTERS = ["core.routers.LegacyRouter"]
# ---------------------end Legacy database configuration----------------------

# ------------------------------------CACHE-----------------------------------
# En servidor: Redis compartido (ya corre en el EC2), respalda los índices
# del mapa con TTL de 24 h. En local (IS_LOCAL): caché en memoria, para no
# exigir un Redis corriendo en Windows. rebuild_map_index refresca a diario.
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1")
if getenv_bool("IS_LOCAL", False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
# ----------------------------------end CACHE---------------------------------

# ---------------------------------SECURITY-----------------------------------

SECRET_KEY = "***REMOVED***"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROXY_KEY = os.getenv("PROXY_KEY")

# PressReader credentials (para scraper de Proceso)
PRESSREADER_USER = os.getenv("PRESSREADER_USER")
PRESSREADER_PASS = os.getenv("PRESSREADER_PASS")
OPENAI_TOKENS_MAX_LENGTH = getenv_int("OPENAI_TOKENS_MAX_LENGTH", 128000)
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE", "gpt-4o")
GEMINI_ENGINE = os.getenv("GEMINI_ENGINE", "gemini-3.5-flash-lite")
SHOW_TEST_PROMPTS = getenv_bool("SHOW_TEST_PROMPTS", False)

ALLOWED_HOSTS = getenv_list("ALLOWED_HOSTS", ["*"])
DEBUG = True
IS_LOCAL = getenv_bool("IS_LOCAL", False)

# Base remota de los archivos legados (NoteFile.file) cuando se corre en
# local: los PDF viejos no están en disco local, solo en S3. Se concatena
# con file.name (p. ej. note_file/123/x.pdf), por eso incluye el prefijo
# data_files (AWS_LOCATION del bucket)
LEGACY_FILES_BASE_URL = os.getenv(
    "LEGACY_FILES_BASE_URL",
    "https://ocsa-docs-032892915740-us-west-2-an.s3.us-west-2"
    ".amazonaws.com/data_files")

# ALLOWED_HOSTS_ENV = os.getenv("ALLOWED_HOSTS")
# ALLOWED_HOSTS = []
# if ALLOWED_HOSTS_ENV:
#     ALLOWED_HOSTS = [
#         host.strip() for host in ALLOWED_HOSTS_ENV.split(",") if host.strip()
#     ]
# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

_CSRF_TRUSTED_ORIGINS = getenv_list("CSRF_TRUSTED_ORIGINS")
if _CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = _CSRF_TRUSTED_ORIGINS

CORS_ORIGIN_ALLOW_ALL = True
# USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_HOST = getenv_bool("USE_X_FORWARDED_HOST", True)
HTTP_X_FORWARDED_HOST = os.getenv("HTTP_X_FORWARDED_HOST")


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -------------------------------END SECURITY---------------------------------


LANGUAGE_CODE = "es-mx"

TIME_ZONE = "America/Mexico_City"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ------------------------------FILE STORAGE----------------------------------
# Documentos de NoteFile/ProjectFile (alias "docs"): en producción van a
# S3 con clase INTELLIGENT_TIERING (baja sola de tier tras 30/90 días sin
# acceso) y lectura pública vía bucket policy sobre AWS_LOCATION. En local
# USE_S3_FILES=0 mantiene el FileSystemStorage de siempre. Las credenciales
# (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY) las toma boto3 del entorno.
USE_S3_FILES = getenv_bool("USE_S3_FILES", False)
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-west-2")
AWS_LOCATION = os.getenv("AWS_LOCATION", "data_files")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
if USE_S3_FILES:
    # custom_domain: fuerza el endpoint regional en file.url; sin él,
    # boto3 genera el endpoint global y S3 responde 307 (redirect) en
    # buckets fuera de us-east-1
    _s3_domain = (
        f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com")
    STORAGES["docs"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "custom_domain": _s3_domain,
            "location": AWS_LOCATION,
            # ACLs deshabilitadas en la práctica: el acceso público lo da
            # la bucket policy, no una ACL por objeto
            "default_acl": None,
            "querystring_auth": False,
            "file_overwrite": False,
            "object_parameters": {"StorageClass": "INTELLIGENT_TIERING"},
        },
    }
else:
    STORAGES["docs"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
# ----------------------------end FILE STORAGE--------------------------------


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "SEARCH_PARAM": "q",
    "DEFAULT_PERMISSION_CLASSES": ("api.permissions.IsFullEditorOrReadOnly",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

CELERY_TASK_RESULT_EXPIRES = getenv_int("CELERY_TASK_RESULT_EXPIRES", 3600)


LAJORNADA_SOURCE_ID = os.getenv("LAJORNADA_SOURCE_ID", 2)
