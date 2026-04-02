# Entidad: Megaproyecto y Estatus

Obra física de gran escala que ocupa o transforma un territorio para extracción o explotación de recursos (presa, mina, gasoducto, parque eólico, desarrollo inmobiliario, etc.). Puede ser componente de un proyecto padre (`parent_project`). Los proyectos con `is_grouper=True` son nodos de agrupación, no proyectos concretos.

## Modelos principales

- **`project.Project`** — registro central del megaproyecto. Tiene `name`, `parent_project` (FK a sí mismo), `conflict` (FK), `megaproject_type` (FK), `is_grouper`, `status_project` (FK).
- **`project.Conflict`** — conflicto socioambiental que agrupa proyectos.
- Ubicaciones geográficas viven en `space_time` como relación inversa `project.locations`.

### Historial de Estatus (StatusHistory)
Registro de un cambio en la etapa del proyecto tal como se menciona en una nota. Permite trazar la evolución del proyecto a través de las notas que lo cubren.

- **`source.StatusHistory`** — vive en el módulo `source/` porque se genera por nota (mención), no es un campo directo del proyecto. Campos: `mention` (FK), `status_project` (FK), `date` (aproximada, nullable), `comments`.

## Catálogos

**`ExtractivismType`** (CatalogGroup) — categoría amplia de industria: `agro`, `mineria`, `hidricos`, `energia`, `urbano`, `infra`.

**`MegaprojectType`** (CatalogType → ExtractivismType) — tipo concreto de proyecto (ej. "Presa hidroeléctrica", "Mina de plata", "Parque eólico").
Un tipo puede cruzar varias categorías extractivas (M2M).

**`StatusProject`** (CatalogType) — etapas del ciclo de vida. 
Valores habituales: `planeación` · `construcción` · `activo` · `ampliación` · `suspensión` · `cancelado` · `clausurado`.

> **Nota sobre el estatus:** El estatus actual del proyecto (`Project.status_project`) referencia este catálogo y se actualiza editorialmente; por otro lado, el historial (`StatusHistory.status_project`) refleja exclusivamente lo que indica cada nota en el tiempo.
