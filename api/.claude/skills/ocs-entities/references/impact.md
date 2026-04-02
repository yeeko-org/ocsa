# Entidad: Afectación (Impact)

Consecuencia **negativa y directa** de la construcción, ampliación u operación de un megaproyecto. Solo se registran afectaciones causadas por el proyecto, no efectos macroeconómicos, accidentes circunstanciales ni desastres externos.

El flag `is_potential` distingue si ya ocurrió (`False`) o podría ocurrir (`True`).

## Modelos principales

- **`impact.Impact`** — registro de una afectación en una mención.
  Campos clave: `mention` (FK), `impact_type` (FK), `impact_subtype` (FK, opcional), `description`, `is_potential` (bool).
- Las ubicaciones de la afectación se registran en `space_time` solo cuando difieren de la ubicación principal del proyecto.
- Si el impacto implica desplazamiento de personas, puede tener un `df.Displacement` relacionado (ver `references/displacement.md`).

## Catálogos

**`ImpactGroup`** — dos grupos fijos:

| id | nombre | Alcance |
|----|--------|---------|
| 1 | Social | Desplazamiento, salud pública, medios de vida, derechos humanos, patrimonio cultural |
| 2 | Ecológico | Contaminación agua/suelo/aire, deforestación, biodiversidad, ecosistemas |

**`ImpactType`** (CatalogType → ImpactGroup) — tipo concreto de afectación dentro de un grupo. Solo se usan los que tienen `status_validation='validated'`. El campo `has_displacement` indica si este tipo puede generar un `Displacement`.

**`ImpactSubtype`** (CatalogType → ImpactType) — subtipo opcional para mayor
precisión dentro del tipo.