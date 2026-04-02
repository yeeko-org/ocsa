# Entidad: Evento (Event)

Hecho narrado en la nota que afecta al proyecto o a sus actores. Los eventos se clasifican en cuatro grupos mutuamente excluyentes según su naturaleza y dirección.

## Modelos principales

- **`event.Event`** — registro del evento en una mención. Campos clave: `mention` (FK), `event_type` (FK), `purpose` (FK, solo para grupo legal),
  `description`, `date` (aproximada), `number_women/men/mix`.
- **`event.Involved`** — vínculo entre un `Participant` y un `Event`. Campos: `event` (FK), `participant` (FK), `involved_role` (FK, opcional),
  `number_women/men/mix`.
- Las ubicaciones del evento se registran en `space_time` solo si difieren de la ubicación principal del proyecto.

## Los 4 grupos de evento

| Grupo | `EventGroup.id` | `Purpose.id` | Descripción |
|-------|----------------|--------------|-------------|
| `collective_actions` | 2 | — | Movilizaciones contra el proyecto: protestas, bloqueos, denuncias, comunicados |
| `acts_of_violence` | 1 | — | Acciones intencionales contra opositores: amenazas, agresiones, criminalización, asesinatos |
| `spoliation_acts` | 3 | 1 | Mecanismos legales que facilitan el despojo (normativas, vacíos jurídicos) |
| `defense_acts` | 3 | 2 | Mecanismos legales en defensa de comunidades (amparos, recursos jurídicos) |

`spoliation_acts` y `defense_acts` comparten `EventGroup` (id=3, name='Mecanismos legales') y se distinguen por el campo `purpose`.

## Catálogos

**`EventGroup`** (CatalogGroup) — los 4 grupos descritos arriba. Tiene `is_conflict_related` y `show_position` (si aplica posicionar actores).

**`EventType`** (CatalogType → EventGroup) — tipo concreto dentro del grupo (ej. "Protesta", "Bloqueo", "Amparo", "Amenaza"). `has_displacement` indica si puede generar un `Displacement`.

**`Purpose`** (CatalogGroup) — propósito del mecanismo legal: despojo o defensa. Solo aplica cuando `EventGroup.id = 3`.

**`InvolvedRole`** (CatalogType) — rol del participante en el evento (ej. "Organizador", "Víctima", "Demandante").