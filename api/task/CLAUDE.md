# `task/` — actividad de los capturistas y horas trabajadas

Mide cuánto trabaja cada usuario en la plataforma sin que nadie registre una jornada: la app guarda huellas de actividad (clics en el dashboard, bloques de scrapeo, tareas fuera de la plataforma) y de ahí deriva *grupos de gasto* (`spend_groups`), intervalos continuos de trabajo cuya suma son las horas del día. Alimenta la vista `dashboard/activity` del front, usada para controlar y pagar el trabajo del equipo de captura.

## Modelo de datos (`models.py`)

- **`ClickHistory`** — una fila por interacción relevante con un registro: `user`, `date_start` (`auto_now_add`; es el único sello de tiempo, no hay fin), `action` (`opened` / `created` / `updated` / `mention_child`) y cuatro FK opcionales y mutuamente excluyentes que dicen sobre qué se actuó: `note`, `article`, `project`, `location`.
- **`OfflineTask`** — trabajo declarado a mano que no deja huella en la plataforma: `date_start`, `date_end`, `activity_type` (`OFFLINE_TYPES`: reunión semanal, reunión, capacitación, otro), `name` opcional, M2M `users` (una tarea puede cubrir a varias personas) y `user_added`.
- **`ScrapedRecord`** — tercer insumo, vive en `source/models.py:230`: cada bloque de scrapeo tiene `user`, `date_start` y `date_end` reales.

Los clics no los crea el front: los escribe el servidor desde `ClickHistoryMixin` (`api/api/views/common_views.py:60`), que cada ViewSet activa declarando `click_actions`. Hoy solo `ArticleViewSet` (`opened`), `NoteViewSet` (`opened`, `updated`), `ProjectViewSet` (`opened`, `created`, `saved`) y las altas de menciones, que se atribuyen a la nota padre con la acción `mention_child`. Que la lista sea corta es intencional: cada acción extra infla las horas.

## Cómo se derivan las horas

Un clic es un instante, no un intervalo, así que el tiempo se reconstruye en dos pasos: primero se le da a cada actividad una duración *acolchonada*, luego se fusionan las que se traslapan.

**1. Acolchonamiento** (`api/api/views/task/serializers.py:19`). `ActivitySerializer` expone `real_start = date_start − pad_before` y `real_end = date_end + pad_after`, con el par `reals` (minutos) distinto por tipo de actividad:

| Actividad | `reals` (antes, después) | `date_end` |
|---|---|---|
| `ScrapedRecord` (`activity_type: "task"`) | 5, 10 | el real del bloque |
| `ClickHistory` (`"click"`) | 3, 8 | inexistente → `date_start + 5 s` |
| `OfflineTask` (`"offline"`) | 8, 12 | el declarado |

El colchón es la hipótesis de trabajo: un clic supone 3 minutos de trabajo previo y 8 posteriores. De ahí sale la tolerancia a huecos, que no está declarada como umbral en ninguna parte sino que **emerge de la suma de los colchones vecinos**: dos clics se fusionan si distan menos de 8 + 3 = 11 minutos; entre un scrapeo y un clic la tolerancia es 10 + 3 = 13; entre dos tareas offline, 20.

**2. Fusión** (`activity.py`, `BuildSpendGroups`). Con las actividades ordenadas por `real_start` ascendente (`api/api/views/task/__init__.py:73`), una sola pasada: si el `real_start` de la siguiente supera el `end` del grupo abierto, cierra el grupo y abre otro; si no, extiende el `end` al máximo. Cada grupo cerrado guarda `start`, `end` y `seconds`. Salen intervalos disjuntos y la suma de sus `seconds` son las horas trabajadas.

Consecuencias al usar estos números:

- Toda sesión aislada cuesta el colchón completo — un clic suelto vale 11 min 5 s. Con actividad dispersa la métrica sobreestima; con actividad densa converge al tiempo real.
- `seconds` usa `timedelta.seconds` (`activity.py:13`), que descarta los días: un grupo de más de 24 h se contaría mal. Hoy no ocurre, pero es un límite, no una decisión.
- `clean_activities` borra `real_start`/`real_end` antes de responder: el front recibe las actividades con sus tiempos originales y los grupos ya calculados, nunca los acolchonados.
- `rebuild_spend_groups` (segunda pasada de fusión sobre los grupos ya formados) está escrita pero desactivada; con la entrada ordenada es redundante.

## Endpoints

- `GET /activity/?days_ago=60&user=<id>` → `ActivityView` (`api/api/views/task/__init__.py:45`): devuelve `{activities, spend_groups}` del usuario autenticado uniendo las tres fuentes filtradas por `date_start >= now − days_ago`. El parámetro `user` solo se respeta si quien pregunta es `is_staff`.
- `offline_task/` → `OfflineTaskViewSet`, alta y edición de tareas offline (fija `user_added` con el usuario de la petición).
- `ClickHistoryViewSet` existe en el mismo archivo pero **no está registrado** en `api/api/urls.py`: los clics no se crean por API.

## Consumo en el front

`nuxt/components/dashboard/activity/`, montado en `pages/dashboard/activity.vue`; `activities` y `spend_groups` viven en el store principal (`store/index.js:472`, `fetchActivities`).

- `ActivityHolder.vue` arma el calendario. El día no es el natural: cada actividad y cada grupo se asignan restando 5 horas a su inicio (`start.subtract(5, 'hours')`), así la jornada corre de 05:00 a 05:00 del día siguiente y una madrugada de trabajo cuenta para el día anterior. Las horas del día son `sum(group.seconds) / 3600` — el front no recalcula nada, solo suma lo que devolvió la API — y acumula horas por semana cerrando el domingo.
- `ActivityViz.vue` dibuja cada día como una línea de tiempo d3 de 04:50 a 05:10 del día siguiente: los `spend_groups` como banda de fondo y las actividades en tres carriles por tipo (offline, click, task), coloreadas por subtipo (`offline_type`) o por modelo tocado (`model`).
- `OfflineEdit.vue` es el diálogo para declarar tareas offline sobre un día del calendario.
