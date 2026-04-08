# Consultas de investigacion — OCSA

Scripts de R para explorar los datos del Observatorio de
Conflictos Socioambientales directamente desde RStudio.

## Requisitos

- **R** version 4.0 o superior
- **RStudio** (recomendado)
- Acceso a la base de datos PostgreSQL del proyecto

## Instalacion

1. Abre RStudio
2. Abre el archivo `config.R`
3. Ejecuta las lineas de `install.packages` (solo la primera vez)
4. Edita las credenciales de conexion con los datos que te
   proporcionaron

## Uso

Cada script es independiente. Para ejecutar cualquier consulta:

1. Abre el script que te interese (por ejemplo
   `actors_by_event.R`)
2. Selecciona todo el codigo (Ctrl+A) y ejecutalo (Ctrl+Enter)
3. Los resultados quedaran como tablas en tu panel de
   **Environment** de RStudio

## Scripts disponibles

| Script | Descripcion |
|--------|-------------|
| `actors_by_event.R` | Actores involucrados en mecanismos legales, con conteos por tipo de mecanismo y proposito (despojo/defensa) |
| `events_by_extractivism.R` | Mecanismos legales cruzados con tipo de extractivismo |
| `legal_vs_impacts.R` | Co-ocurrencia entre mecanismos legales y afectaciones (sociales y ambientales), con indicador lift |
| `legal_vs_opposition.R` | Co-ocurrencia entre mecanismos legales y eventos de oposicion (violencias, acciones colectivas), con indicador lift |

## Nota sobre el indicador lift

Los scripts `legal_vs_impacts.R` y `legal_vs_opposition.R`
calculan un indicador llamado **lift**:

- **lift > 1**: la combinacion ocurre *mas* de lo esperado
- **lift = 1**: ocurre con la frecuencia esperada
- **lift < 1**: ocurre *menos* de lo esperado

Esto permite identificar asociaciones atipicas entre mecanismos
legales y otros tipos de eventos o afectaciones.
