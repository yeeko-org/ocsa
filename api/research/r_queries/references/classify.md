# Catálogos transversales

Catálogos usados por varias entidades del sistema: sectores, tipos de
participación, pertenencias, países, grupos indígenas e intereses. La
mayoría tiene `status_validation` (FK por nombre a
`work_flux_statuscontrol`); **por defecto no se filtra** al consultar.

## Sectores de actores (dos niveles)

Un actor pertenece a un **sector** (`classify_sector`), y cada sector
vive dentro de un **grupo de sectores** (`classify_sectorgroup`).

### `classify_sectorgroup`

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `is_collective` | bool |
| `has_belongs` | bool |
| `capital_type` | text |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

Ejemplos: "Institución federal", "Empresa privada", "Ciudadanía
organizada".

### `classify_sector`

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `sector_group_id` | integer → `classify_sectorgroup.id` |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

Ejemplo: sector "Secretaría de la Defensa" dentro del grupo
"Institución federal".

## Tipos de participación y posición (dos niveles)

Cada participante tiene uno o varios **tipos de participación**, y de
cada tipo se deriva su **posición** respecto al proyecto (a favor, en
contra, neutral, etcétera).

### `classify_participantgroup`

Agrupa tipos afines.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `short_name` | text |

### `classify_participanttype`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | |
| `name` | text | |
| `position` | text | `support`, `oppose`, `neutral`, `other`, `undefined` |
| `participant_group_id` | integer → `classify_participantgroup.id` | |
| `required_interests` | bool | Si exige registrar el interés del participante |
| `status_validation_id` | text → `work_flux_statuscontrol.name` | |

La **posición** del participante se lee de `position` del tipo. Un
participante puede tener varios tipos en
`actor_participant_participant_types`, por lo que la posición se
evalúa por cada tipo, no al nivel del actor.

## Pertenencias / vulnerabilidades

### `classify_belong`

Catálogo plano, cerrado. Etiquetas que marcan condición del actor
(afectado, habitante, indígena, campesino, líder, trabajador, urbano,
organización de mujeres, participación sobresaliente de mujeres, tiene
protección).

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `short_name` | text |
| `description` | text |

Relación con actor: M2M mediante `actor_actor_belongs`.

## Grupo indígena

### `classify_indigenousgroup`

Catálogo plano.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

Un actor referencia uno mediante `actor_actor.indigenous_group_id`.

## Países

### `classify_country`

Catálogo plano. Usado en dos contextos: países de origen del actor
(M2M `actor_actor_countries`) y país destino en desplazamiento
internacional (`df_displacement.destination_country_id`).

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `flag_emoji` | text |

## Intereses (tres niveles)

Sistema jerárquico para describir la motivación de un participante en
el proyecto: **grupo → tipo → subtipo**.

### `classify_interestgroup`

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |

### `classify_interesttype`

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `interest_group_id` | integer → `classify_interestgroup.id` |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

### `classify_interestsubtype`

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `interest_type_id` | integer → `classify_interesttype.id` |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

Un `actor_interest` apunta a un subtipo (`interest_subtype_id`) y
puede incluir texto libre en `text`.

## Ejemplos

### Conteo de participantes por posición

```sql
SELECT
    tt.position,
    COUNT(DISTINCT p.id) AS n_participaciones
FROM actor_participant p
JOIN actor_participant_participant_types pt
                                  ON pt.participant_id = p.id
JOIN classify_participanttype tt
                                  ON tt.id = pt.participanttype_id
GROUP BY tt.position
ORDER BY n_participaciones DESC
```

### Actores indígenas con su grupo y sector

```sql
SELECT
    a.name,
    ig.name AS grupo_indigena,
    s.name  AS sector
FROM actor_actor a
LEFT JOIN classify_indigenousgroup ig ON ig.id = a.indigenous_group_id
LEFT JOIN classify_sector          s  ON s.id = a.sector_id
WHERE a.indigenous_group_id IS NOT NULL
```

## Trampas frecuentes

- El `position` del participante se obtiene de
  `classify_participanttype`, no de `classify_participantgroup`.
- Un participante puede tener varios tipos a la vez. Para "actores
  que se oponen", basta con que uno de sus tipos tenga
  `position = 'oppose'`.
- Los catálogos de `classify` tienen `status_validation`, pero por
  defecto no se filtran (ver `esquema_bd.md`).
