# Instrucciones al agente

Este archivo gobierna cómo el agente colabora con la usuaria dentro de
esta carpeta. Todo lo que genere el agente es **R + SQL** para ejecutar
contra PostgreSQL usando el patrón `conectar_bd()` + `consulta(con, sql)`
de `config.R`.

## 1. Rondas de aclaración antes de generar una query

Al inicio de una tarea, si hay ambigüedad en el prompt, el agente hace
una ronda breve de preguntas y explica **por qué** pregunta (tono
pedagógico). La idea es que la usuaria aprenda el modelo de datos a
medida que trabaja. Si el prompt ya resuelve la ambigüedad, no
preguntar.

Casos canónicos a vigilar:

- **Ubicación de algo**. Cada entidad (proyecto, evento, afectación)
  puede tener su propia fila en `space_time_location`, filtrando por
  `project_id`, `event_id` o `impact_id`. Para una misma entidad con
  varias ubicaciones registradas, se elige la de mayor
  `status_location.priority` (patrón canónico del sistema).

  Para **evento y afectación** hay dos niveles posibles de ubicación:

  a) **Directa**: la fila de `space_time_location` ligada al propio
     `event_id` o `impact_id`. Suele estar poco poblada y no siempre
     existe.
  c) **Vía proyecto** (`mention → project → space_time_location`):
     la ubicación principal del proyecto al que pertenece la nota.
     **Este es el default** cuando la usuaria pide "la ubicación del
     evento o la afectación": es la ruta más
     poblada.

  Comportamiento del agente para evento/afectación: **no preguntar**,
  usar la opción c) por default y **mencionarlo explícitamente** en el
  resumen de la respuesta, de modo que la usuaria pueda pedir la
  opción a) o un `COALESCE` entre ambas si le conviene.

  Para **desplazamiento forzado** la ubicación funciona distinto y
  tiene varios niveles (origen, destino, ubicación del evento o
  afectación asociados, ubicación del proyecto). El caso es
  multidimensional y no tiene default limpio, así que **sí
  preguntar**. El menú completo de opciones y el patrón SQL viven en
  `references/df.md` (sección "Ubicación en desplazamiento: menú de
  opciones"); cargar ese archivo antes de generar la query y
  presentarle a la usuaria las opciones documentadas ahí.

- **Despojo vs defensa**. Ambos mecanismos legales conviven en
  `event_event` con `event_type.event_group_id = 3`. Se distinguen por
  `event_event.purpose_id`: `1` = despojo, `2` = defensa. Si la usuaria
  dice "mecanismos legales" sin precisar, preguntar si quiere ambos,
  solo despojo o solo defensa.

- **Actor relacionado con un evento: directo o indirecto**. La tabla
  `event_involved` registra la relación directa (este actor participó
  en este evento). La alternativa indirecta es la co-ocurrencia en la
  misma nota (mismo `source_mention`): el actor aparece mencionado en
  la misma nota donde se reportó el evento, sin que necesariamente
  haya participado. Son preguntas semánticamente distintas; preguntar
  cuál quiere. Por defecto, si la usuaria dice "actores involucrados
  en el evento", asumir directo vía `event_involved`.

## 2. Pregunta única sobre validación

Al inicio de una tarea, hacer una sola pregunta: **"¿Quieres limitar
los resultados a proyectos y notas ya validados/públicos?"**. Por
defecto, si la usuaria no responde afirmativamente, **no filtrar**.

Si la respuesta es sí:

- Cuando el modelo principal de la query sea `project_project`,
  aplicar:
  ```sql
  JOIN work_flux_statuscontrol sc
       ON sc.name = project_project.status_validation_id
  WHERE sc.is_public = TRUE
  ```
- Para cualquier otro modelo principal (Event, Impact, Actor,
  Participant, Displacement, etc.), buscar la ruta más corta a
  `source_mention` y filtrar por el `status_register` de la nota
  asociada:
  ```sql
  JOIN source_note       n  ON n.id = source_mention.note_id
  JOIN work_flux_statuscontrol sc
       ON sc.name = n.status_register_id
  WHERE sc.is_public = TRUE
  ```

**No** aplicar este filtro a catálogos (tipos, subtipos, grupos). Los
catálogos tienen su propio `status_validation` en varios casos, pero
filtrarlos por defecto confunde y resta datos. Documentarlo en las
referencias, pero no preguntarlo.

Nota: `work_flux_statuscontrol` usa el campo `name` (texto) como clave
primaria, no un `id` numérico.

## 3. Regla evolutiva

Cuando la usuaria muestre que ya internalizó un patrón (p. ej., ya
distingue por su cuenta "grupo de evento" de "tipo de evento", o ya
dice directamente "defensa" en vez de "mecanismos legales"), el agente
puede **editar este mismo archivo** para relajar la regla
correspondiente: cambiar "siempre preguntar" por "preguntar solo si el
prompt es ambiguo".

Cada vez que relaje una regla, agregar una línea en la **Bitácora** al
pie de este archivo con la fecha y el motivo.

## 4. Carga selectiva de referencias

Antes de generar SQL, cargar **solo** los archivos de `references/`
relevantes al prompt, no todos. El índice para decidir qué cargar está
en `esquema_bd.md` (sección "Dónde buscar cada cosa").

## 5. Estilo de la respuesta

- Primero un resumen en una o dos líneas de lo que se va a consultar.
- Luego el bloque SQL comentado por pasos.
- Luego el snippet R con el patrón `consulta(con, sql)` y el
  post-procesado (dplyr) cuando aplique.
- Al final, recordar `dbDisconnect(con)` si el script abre su propia
  conexión.
- Si la usuaria ejecutó la query y obtuvo resultados inesperados,
  diagnosticar con preguntas antes de modificar el SQL.

---

## Bitácora

Entradas al pie del archivo cuando una regla se relaja o se agrega por
aprendizaje. Formato: `AAAA-MM-DD — qué cambió y por qué`.
