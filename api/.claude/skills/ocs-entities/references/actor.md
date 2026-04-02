# Entidad: Actor / Participante

Persona, comunidad u organización con relación directa y explícita con un proyecto. Se captura con una **posición** respecto al proyecto: se opone (`oppose`), lo apoya/ejecuta (`support`), o media entre partes (`neutral`).

## Modelos principales

- **`actor.Actor`** — registro permanente y reutilizable.
  Campos clave: `name`, `sector` (FK), `belongs` (M2M → Belong), `indigenous_group` (FK), `parent_actor` (FK a sí mismo), `geo_reach`.
- **`actor.Participant`** — vínculo entre un `Actor` y una `Mention`. Un mismo actor puede participar en múltiples menciones con distintas posiciones. Tiene `participant_types` (M2M → ParticipantType).
- **`actor.Interest`** — interés específico del participante en esa mención.
  Campos: `text` (descripción libre), `interest_subtype` (FK, opcional).
- **`actor.Member`** — relación entre un actor individual y uno colectivo(`actor_individual`, `actor_collective`, `membership_type`).

## Catálogos vinculados a Participant:

**`ParticipantGroup`** / **`ParticipantType`** (CatalogGroup/Type) — clasifican el tipo y posición del participante en el proyecto. Mapeo de `ParticipantGroup`: `oppose → 1`, `neutral → 2`, `support → 3`.

**`InterestGroup`** / **`InterestType`** / **`InterestSubtype`** — jerarquía de tres niveles para clasificar el tipo de interés del participante en el proyecto.

## Catálogos vinculados al Actor:

**`SectorGroup`** / **`Sector`** (CatalogGroup/Type) — sector o ámbito al que pertenece el actor (ej. "Institución federal", "Empresa privada", "Ciudadanía Organizada").

**`Belong`** (CatalogBase) — grupos de vulnerabilidad o identidad a los que pertenece el actor. Valores fijos:
`Afectado` · `Habitante` · `Indígena` · `Campesino` · `Líder` · `Trabajador` · `Urbano` · `Organización de mujeres` · `Participación sobresaliente de mujeres` · `Tiene Protección`.

**`IndigenousGroup`** — pueblo o nación indígena específica.
