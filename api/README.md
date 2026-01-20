

## Pasos iniciales:
- Tener instalado Python 3, mínimo 3.13

- instalar pip (normalmente ya viene con python)

- Revisar que las variables de entorno se escribieron adecuadamente (Si se trabaja en Windows)

## Entornos virtuales
- Preferentemente, tener dos carpetas separadas (para una mejor organización):
- La primera para los entornos virtuales, y otro para los sistemas/proyectos

- Instalar venv
- Crear en ambiente virtual, en este caso llamado 'escaleras' en la carpeta env:
```bash
python -m venv ocsa
````

- Iniciar el entorno virtual (venv) en la carpeta colocada
```
# en Windows
.\ocsa\Scripts\Activate.ps1
# o en Linux/Mac
source ocsa/bin/activate
```

## Variables de entorno
- Crear un archivo .env en la carpeta dev\ocsa con las variables de entorno necesarias (puedes basarte en el archivo .env.example)

## Instalación de paquetes requeridos
- Instalar los paquetes requeridos para el sistema en la carpeta dev\ocsa.  (Esto viene en el archivo requirements.txt)
```bash
pip install -r requirements.txt
```


## Base de datos


### Opción PostgreSQL (Para producción o equipos que ya lo usan)

- Deberás tener instalado PostgreSQL
- Crear una base de datos en PostgreSQL llamada 'escaleras-local' (o el nombre que desees)
- Configurar tu archivo `.env` con las credenciales de PostgreSQL:
  ```env
  POSTRGRESQL_DB=True
  DATABASE_NAME=ocsa-local
  DATABASE_USER=tu_usuario
  DATABASE_PASSWORD=tu_contraseña
  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  DATABASE_SCHEMA=public
  ```
  
Crear la extensión unaccent en PostgreSQL
```bash
CREATE EXTENSION IF NOT EXISTS unaccent;
```


Los datos de ubicación tienen que cargarse primero antes de las migraciones de datos

Órden de ejecución de migración de datos:

python manage.py migrate
python manage.py migrate_initial_data

(OPCIONAL) Migrar los usuarios de la base de datos de producción

python manage.py migrate_ps_schemas

python manage.py load_states_data
python manage.py load_municipios
python manage.py load_localidades
python manage.py migrate_ubicaciones
python manage.py migrate_notas
python manage.py migrate_proyectos
python manage.py migrate_classify
python manage.py migrate_events
python manage.py migrate_afectaciones
python manage.py migrate_opositores_participation
python manage.py migrate_proyectos_status
python manage.py migrate_legacy_users

python manage.py migrate_coordinates /path/
python manage.py migrate_project_files --source /path/ --output migrate_project_files_exit.json
python manage.py migrate_note_files --source /path/ --output migrate_note_files_exit.json

python manage.py datum_recovery
python manage.py post_legal_resources


## Correr el servidor localmente
- Antes de correr el servicio, genera los archivos estáticos con el siguiente comando:
```bash
python manage.py collectstatic
```

## Crear un superuser para poder entrar al admin
```bash
python manage.py createsuperuser
```

- Correr el servidor localmente con el siguiente comando:
```console
python manage.py runserver
```
- Acceder a la aplicación en el navegador web en la dirección http://localhost:8000/admin
- Acceder al API Explorer en el navegador web en la dirección http://localhost:8000/api


### Ayudas adicionales:
ID a partir del cual son borradores: 3915

from source.models.models import Note
Note.objects.filter(id__gte=3915).update(status_register='created')
