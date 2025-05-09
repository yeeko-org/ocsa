# ocs django db

los datos de ubicacion tienen que cargarse primero antes de las migracion de datos

orden de ejecucion de migracion de datos:

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

ID a partir del cual son borradores: 3915

from source.models.models import Note
Note.objects.filter(id__gte=3915).update(status_register='created')
