# Notas, menciones y fuentes

La unidad básica del sistema es la **nota periodística**
(`source_note`). Una nota puede hablar de uno o varios proyectos: por
cada proyecto mencionado en la nota se crea una fila en
`source_mention`. Esa mención es el hub al que cuelgan actores,
eventos y afectaciones.

## Tablas

### `source_note`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `title` | text | Título de la nota |
| `subtitle` | text | |
| `date` | date | Fecha de la nota (publicación o captura) |
| `capture_date` | date | Fecha en que se capturó en el sistema |
| `link` | text | URL original |
| `source_id` | integer → `source_source.id` | Medio/fuente |
| `editor_id` | integer → `profile_auth_user.id` | Editor principal |
| `reviewer_id` | integer → `profile_auth_user.id` | Revisor |
| `status_register_id` | text → `work_flux_statuscontrol.name` | Estatus editorial/validación |
| `pre_mentions` | jsonb | Menciones candidatas antes de curaduría |
| `frozen_pre_capture` | bool | Si bloquea reprocesamiento |

**M2M adicionales** (editores y revisores múltiples):

- `source_note_editors` (`note_id`, `user_id`).
- `source_note_reviewers` (`note_id`, `user_id`).

### `source_mention`

Nota × proyecto. Una fila por cada proyecto mencionado en una nota.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `note_id` | integer → `source_note.id` |
| `project_id` | integer → `project_project.id` |

Todos los eventos, afectaciones y participantes cuelgan de una
mención vía `mention_id`.

### `source_source`

Medios periodísticos (catálogo).

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `is_news` | bool |
| `main_url` | text |
| `order` | integer |

Ejemplos: La Jornada, Reforma, Proceso.

### `source_statushistory`

Historial de cambios de estatus del proyecto, registrados por
mención. Útil para series de tiempo de cómo ha evolucionado el
proyecto según lo narrado.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `mention_id` | integer → `source_mention.id` |
| `status_project_id` | text → `project_statusproject.name` |
| `date` | date (nullable) |
| `comments` | text |

### `source_notefile`

Archivos adjuntos a la nota (PDFs, capturas).

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `note_id` | integer → `source_note.id` |
| `file` | text |

### `source_article`

Artículo crudo extraído por raspado. Para efectos de consulta se usa
solo como complemento de la nota: una nota tiene en la práctica un
único artículo asociado (la tabla permite varios, pero no suele
darse).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `note_id` | integer → `source_note.id` (nullable) | Nota a la que dio origen |
| `basic_content` | text | Texto plano de la nota |
| `paragraphs` | jsonb | Párrafos curados en JSON |
| `images` | jsonb | Imágenes curadas en JSON |

El resto de campos del artículo (criterios de scoring, scraping,
estatus de revisión) es procedimental y no interesa para el análisis
de conflictos.

## Ejemplos

### Proyectos con conteo y rango de notas

```sql
SELECT
    p.id,
    p.name,
    COUNT(DISTINCT n.id) AS n_notas,
    MIN(n.date)          AS primera_nota,
    MAX(n.date)          AS ultima_nota
FROM project_project p
JOIN source_mention m ON m.project_id = p.id
JOIN source_note    n ON n.id = m.note_id
GROUP BY p.id, p.name
ORDER BY n_notas DESC
```

### Notas con su texto plano del artículo

```sql
SELECT
    n.id,
    n.date,
    n.title,
    a.basic_content
FROM source_note n
LEFT JOIN source_article a ON a.note_id = n.id
WHERE n.date >= DATE '2023-01-01'
```

### Historial de estatus de un proyecto

```sql
SELECT
    sh.date,
    sp.name AS estatus,
    sh.comments
FROM source_statushistory sh
JOIN source_mention   m  ON m.id = sh.mention_id
JOIN project_statusproject sp ON sp.name = sh.status_project_id
WHERE m.project_id = 123
ORDER BY sh.date
```

## Trampas frecuentes

- Una nota puede tener **varias** menciones (una por proyecto). Para
  contar notas únicas al cruzar con otras tablas, usar
  `COUNT(DISTINCT n.id)`.
- `status_register_id` de la nota es el que se usa para filtrar
  "notas validadas/públicas" (ver `esquema_bd.md`).
- `source_note.date` puede diferir de `event_event.date`. La fecha de
  la nota es cuándo se publicó el reporte; la del evento es cuándo
  ocurrió el hecho.
- `source_article.note_id` es nullable y en la práctica hay artículos
  descartados (no convertidos en notas). Para el análisis, usar
  `INNER JOIN` si solo quieres artículos con nota, o `LEFT JOIN` si
  quieres todos.
