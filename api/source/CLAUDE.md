## Dominio: Módulo `source/`

Este módulo gestiona las notas periodísticas (de Jornada, Reforma y Proceso)
que son la fuente primaria de datos del OCSA. Cada nota puede disparar un
proceso de pre-captura asistida por IA que extrae entidades estructuradas.

---

## Modelo conceptual de pre-captura

### Megaproyecto extractivista

Obra, actividad o instalación física de gran escala que ocupa o transforma
un territorio para la extracción, transformación o explotación de recursos
naturales (presas, minas, gasoductos, monocultivos, desarrollos inmobiliarios,
parques eólicos, etc.). Puede ser componente de un proyecto padre
(`parent_project`).

### Entidades extraídas por nota

Una nota puede mencionar uno o varios proyectos. Por cada proyecto mencionado
se genera una **mención** con cinco componentes:

#### 1. `project_full` — Datos del proyecto
Identidad y ubicación del proyecto en la nota: nombre, tipo, ubicaciones
(estado / municipio / localidad / detalles), proyecto padre si aplica.

#### 2. `status_history` — Historial de estatus
Cambios de etapa del proyecto mencionados en la nota: planeación,
construcción, activo, ampliación, suspensión, cancelado, clausurado.
Cada entrada tiene fecha aproximada y referencia a párrafos.

#### 3. `impacts` — Afectaciones

Consecuencias **negativas y directas** de la construcción, ampliación u
operación del proyecto. Dos grupos:

- **Social:** desplazamiento, salud pública, pérdida de medios de vida,
  violación de derechos (consulta, participación), patrimonio cultural.
- **Ecológico:** contaminación (agua/suelo/aire), deforestación, pérdida
  de biodiversidad, alteración de ecosistemas.

**Frontera clave:** solo impacto directo del proyecto. Se descartan efectos
macroeconómicos, accidentes circunstanciales y desastres naturales externos.
Cada impacto tiene un flag `is_potential` (ocurrido vs. posible).

#### 4. `actors` — Actores

Personas, comunidades u organizaciones con relación **directa y explícita**
con el proyecto. Máximo 20. Tres posiciones posibles:

- `oppose` — se oponen al proyecto
- `support` — lo promueven, ejecutan o apoyan
- `neutral` — median entre opositores y promotores

Se descartan actores incidentales (ej. bomberos, protección civil) y
trabajadores sin posición explícita.

Cada actor tiene sector (`sector_text`) y puede pertenecer a grupos
especiales: Afectado, Indígena, Campesino, Habitante, Líder, Trabajador,
Urbano, organización/participación de mujeres, Tiene Protección.

#### 5. `events` — Eventos

Hechos narrados en la nota que afectan al proyecto o a sus actores.
Cuatro grupos mutuamente excluyentes:

| Grupo | Descripción |
|-------|-------------|
| `collective_actions` | Movilizaciones y acciones colectivas **dirigidas contra el proyecto**: protestas, bloqueos, denuncias, comunicados, tomas de instalaciones. |
| `acts_of_violence` | Acciones intencionales para dañar a **opositores**: amenazas, agresiones, criminalización, demandas legales contra opositores, asesinatos. |
| `spoliation_acts` | Mecanismos legales que **facilitan el despojo**: normativas, vacíos o interpretaciones jurídicas que permiten el acceso de actores privados/estatales. |
| `defense_acts` | Mecanismos legales **en defensa de comunidades**: amparos, recursos jurídicos que restringen, cancelan o disminuyen el proyecto. |

Cada evento referencia actores de la lista mediante `involvements` (actor_uid
+ rol). Las ubicaciones solo se registran si difieren de la ubicación
principal del proyecto.