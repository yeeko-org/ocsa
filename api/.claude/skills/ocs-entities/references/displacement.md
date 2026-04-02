# Entidad: Desplazamiento forzado (Displacement)

Registro detallado del desplazamiento de personas o comunidades asociado a un impacto o evento.

## Modelo principal

**`df.Displacement`** — se vincula a un `Impact` o a un `Event` (ambos opcionales). Registra ritmo (Paulatino o Repentino) ubicación y los siguientes catálogos:

## Catálogos

**`Dimension`** — Interno; Internacional.

**`PopulationSize`** — Individuos y/o Familias; Masivo (Comunidades enteras).

**`Temporality`** — Permanente; Temporal.

- Campos de ubicación sobre origen y destino, incluye relación con modelos `Locality`, `Municipality`, `State` y `Country` (si es internacional) de la app `space_time`.
