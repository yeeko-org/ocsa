from pprint import pprint
from .settings import *
from dotenv import load_dotenv
import os
dotenv_path = os.path.join(BASE_DIR, "prod.env")
load_dotenv(dotenv_path=dotenv_path, override=True)

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
        'NAME': os.path.join(BASE_DIR, DATABASE_NAME)
    }

if DATABASE_SCHEMA:
    default_database['OPTIONS'] = {  # type: ignore
        'options': f'-c search_path={DATABASE_SCHEMA}',
    }

DATABASES = {
    "default": default_database
}


print("Loading production settings")
