import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = '***REMOVED***'

DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'profile_auth.User'


# Application definition

INSTALLED_APPS = [
    'ps_schema',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'profile_auth',
    'ocsa_legacy',
    'work_flux',
    'classify',
    'space_time',
    'project',
    'source',
    'actor',
    'impact',
    'event',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_PATH],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# -----------------------Default database configuration-----------------------
POSTRGRESQL_DB = os.getenv('POSTRGRESQL_DB', False)
DATABASE_NAME = os.getenv("DATABASE_NAME", "db.sqlite3")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")
if POSTRGRESQL_DB:
    default_database = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv("DATABASE_HOST"),
        'PORT': int(os.getenv("DATABASE_PORT", 5432)),
    }
else:

    default_database = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / DATABASE_NAME
    }

if DATABASE_SCHEMA:
    default_database['OPTIONS'] = {
        'options': f'-c search_path={DATABASE_SCHEMA}',
    }

DATABASES = {
    "default": default_database
}
# ---------------------end Default database configuration---------------------

# -----------------------Legacy database configuration------------------------
DATABASE_LEGACY_NAME = os.getenv("DATABASE_LEGACY_NAME")
if DATABASE_LEGACY_NAME:
    POSTRGRESQL_LEGACY_DB = os.getenv('POSTRGRESQL_LEGACY_DB', False)
    DATABASE_LEGACY_SCHEMA = os.getenv("DATABASE_LEGACY_SCHEMA")
    if POSTRGRESQL_LEGACY_DB:
        legacy = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': DATABASE_LEGACY_NAME,
            'USER': os.getenv("DATABASE_LEGACY_USER"),
            'PASSWORD': os.getenv("DATABASE_LEGACY_PASSWORD"),
            'HOST': os.getenv("DATABASE_LEGACY_HOST"),
            'PORT': int(os.getenv("DATABASE_LEGACY_PORT", 5432)),
        }
    else:

        legacy = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / DATABASE_LEGACY_NAME
        }

    if DATABASE_LEGACY_SCHEMA:
        legacy['OPTIONS'] = {
            'options': f'-c search_path={DATABASE_LEGACY_SCHEMA}',
        }

    DATABASES["legacy"] = legacy
    DATABASE_ROUTERS = ['core.routers.LegacyRouter']
# ---------------------end Legacy database configuration----------------------


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


LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
