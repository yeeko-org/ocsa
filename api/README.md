# ocs django db

los datos de ubicacion tienen que cargarse primero antes de las migracion de datos

orden de ejecucion de migracion de datos:

python .\manage.py  migrate
python .\manage.py  runserver

python .\manage.py  migrate_ps_schemas

python .\manage.py  load_states_data
python .\manage.py  load_municipios
python .\manage.py  load_localidades
python .\manage.py  migrate_ubicaciones
python .\manage.py  migrate_notas
python .\manage.py  migrate_proyectos
python .\manage.py  migrate_classify
python .\manage.py  migrate_events
python .\manage.py  migrate_afectaciones
python .\manage.py  migrate_proyectos_status
python .\manage.py  migrate_legacy_notes
