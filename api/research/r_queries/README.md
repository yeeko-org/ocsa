# Consultas de investigación — OCSA

Carpeta autocontenida para explorar los datos del **Observatorio de
Conflictos Socioambientales** desde R. La carpeta incluye:

- Scripts de R de ejemplo (`*.R`).
- Un archivo `config.R` con la conexión a la base PostgreSQL.
- Una referencia completa del esquema de la base en `esquema_bd.md` y
  su desarrollo por entidad en la carpeta `references/`.
- Un archivo `CLAUDE.md` con instrucciones para el asistente que
  colabora contigo generando nuevas consultas.

## Requisitos

- **R** versión 4.0 o superior.
- **RStudio** (recomendado).
- Acceso a la base PostgreSQL del proyecto (credenciales que te
  proporcionaron aparte).

## Instalación

1. Abre esta carpeta en RStudio.
2. Abre `config.R`.
3. Ejecuta las líneas de `install.packages(...)` la primera vez.
4. Edita las credenciales de conexión con los datos que te pasaron.

## Dos formas de generar nuevas consultas con Claude

### A. Desde Claude Cowork (más sencillo)

1. Entra a Claude Cowork.
2. Sube o abre esta carpeta como recurso de trabajo.
3. Escribe en lenguaje natural lo que quieres consultar
   (por ejemplo: *"Dame las afectaciones ecológicas en proyectos
   mineros de Oaxaca"*).
4. Claude leerá los archivos de `references/`, te hará una o dos
   preguntas para aclarar la consulta y te devolverá SQL + código R
   listo para pegar en RStudio.

### B. Desde Claude Code dentro de RStudio

1. Instala Claude Code.
2. Abre esta carpeta como proyecto.
3. Conversa con Claude en el panel del asistente. El flujo es el
   mismo que en Cowork; la diferencia es que puede ejecutar los
   archivos directamente.

En ambos caminos, Claude te preguntará al inicio si quieres limitar
los resultados a **proyectos y notas validados/públicos**. Responde
según tu necesidad; por defecto no filtra.

## Uso de los scripts existentes

Cada script es independiente. Para ejecutar cualquiera:

1. Abre el script (por ejemplo `actors_by_event.R`).
2. Selecciona todo (Ctrl+A) y ejecuta (Ctrl+Enter).
3. Los resultados quedarán como tablas (`tibble`) en el panel
   **Environment** de RStudio.

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `actors_by_event.R` | Actores en mecanismos legales, con conteos por tipo y propósito (despojo/defensa). Usa co-ocurrencia por mención (ver comentario al inicio del archivo). |
| `events_by_extractivism.R` | Mecanismos legales cruzados con tipo de extractivismo. |
| `legal_vs_impacts.R` | Co-ocurrencia entre mecanismos legales y afectaciones (sociales y ambientales), con indicador *lift*. |
| `legal_vs_opposition.R` | Co-ocurrencia entre mecanismos legales y eventos de oposición (violencias, acciones colectivas), con indicador *lift*. |
| `displacement_map.R` | Mapa/tabla de registros de desplazamiento forzado con su ubicación de origen y destino. |

## Sobre el indicador *lift*

`legal_vs_impacts.R` y `legal_vs_opposition.R` calculan un indicador
llamado **lift**:

- **lift > 1**: la combinación ocurre *más* de lo esperado por azar.
- **lift = 1**: ocurre con la frecuencia esperada.
- **lift < 1**: ocurre *menos* de lo esperado.

Permite identificar asociaciones atípicas entre mecanismos legales y
otros tipos de eventos o afectaciones.

## Dónde está documentado el esquema de la base

- `esquema_bd.md` — índice, mapa de entidades y caminos de JOIN más
  comunes.
- `references/` — un archivo por entidad (actor, project, event,
  impact, df, space_time, classify, source) con tablas, columnas,
  relaciones y ejemplos.

Cuando le pidas una consulta a Claude, él consultará estos archivos
por ti.
