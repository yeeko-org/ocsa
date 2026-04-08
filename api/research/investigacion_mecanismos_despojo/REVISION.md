# Revisión de la Investigación — Mecanismos de Despojo

Documento de seguimiento para la retroalimentación sistemática de la
investigación "Mecanismos Legales e Institucionales de Despojo en
México". Registra observaciones, problemas y mejoras por sección.

**Preocupaciones centrales del cliente (Ibero):**
- Los datos no son tan impactantes como quisieran
- La unidad de medida ("menciones hemerográficas") es débil

---

## Problema transversal: la unidad de medida

### Diagnóstico

La investigación usa **menciones en fuentes hemerográficas** como
unidad de análisis. Esto tiene implicaciones serias:

1. **Una mención no es un hecho.** Si La Jornada, Proceso y Reforma
   cubren el mismo amparo contra el Tren Maya, eso genera 3 menciones
   pero documenta 1 evento jurídico. No hay control de duplicación.
2. **El sesgo mediático se convierte en sesgo analítico.** Proyectos
   con mayor cobertura (Tren Maya, CIIT, Dos Bocas) concentran
   menciones por visibilidad, no necesariamente por gravedad. Los
   propios autores reconocen esto en cap2_04: "somos conscientes del
   sesgo de representatividad".
3. **Los porcentajes heredan el sesgo.** Decir que el Tren Maya
   concentra el 17.9% de las CLPI para despojo (Gráfica 1, cap2_02)
   no dice si es el proyecto con más violaciones al derecho de
   consulta o simplemente el más cubierto por la prensa.

### Alternativa desde la base de datos del OCSA

La base del OCSA ya modela los mecanismos legales como **eventos
únicos** (`event.Event` con `EventGroup.id=3`), vinculados a:

- **Proyectos** concretos (con tipo extractivo, estatus, ubicación)
- **Participantes** con roles (demandante, demandado, etc.)
- **Propósito**: despojo (`Purpose.id=1`) o defensa (`Purpose.id=2`)
- **Impactos** sociales/ambientales registrados
- **Desplazamientos forzados** cuando aplica

**Propuesta:** La unidad de análisis debería ser **el evento jurídico
documentado**, no la mención. Los 702 registros de menciones podrían
re-expresarse como N eventos distintos (donde N < 702), cada uno
con atributos verificables: tipo de mecanismo, proyecto asociado,
actores, consecuencias documentadas. Esto elimina el problema de la
duplicación y permite análisis más robustos (temporal, geográfico,
por tipo de extractivismo, por actor).

**Estado:** [ ] Pendiente de evaluar con el equipo

---

## Revisión por sección

### Capítulo 1 — Mecanismos Legales de Despojo (MLD)

#### `cap1_01_introduccion.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Dato | 67.09% despojo + 32.19% defensa = 99.28%. Falta explicar el 0.72% restante (¿casos sin clasificar? ¿redondeo?). Con 702 registros: 471 + 226 = 697, faltan 5 |
| 2 | Dato | "presente en más del 60% de los megaproyectos registrados" — ¿cuántos megaproyectos hay en total? Sin denominador, el dato pierde fuerza |
| 3 | Impacto | El dato de MIA (148 despojo vs 5 defensa) es potente pero se presenta de pasada. Merece más desarrollo: ¿en qué proyectos? ¿qué patrón revela? |
| 4 | Gráfica | Gráfica 1 es una imagen sin datos tabulados. No se puede verificar ni reproducir. Debería existir una tabla complementaria |
| 5 | Impacto | Los 130 juicios de amparo en defensa son un hallazgo fuerte. ¿Cuántos fueron exitosos? ¿Cuántos siguen en trámite? Eso haría el dato mucho más impactante |
| 6 | Fuente | Los 18 mecanismos se mencionan pero solo 12 aparecen en la Tabla 1 de cap1_02. ¿Dónde están los otros 6? |

#### `cap1_02_tabla_mecanismos_legales.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Estructura | La tabla tiene 12 mecanismos, no 18 como anuncia cap1_01. Faltan: Juicio Agrario, Cambio de uso de suelo, y posiblemente otros. Esto es una inconsistencia importante |
| 2 | Dato | Ningún mecanismo de la tabla incluye datos cuantitativos (cuántas veces fue usado, en cuántos proyectos). Solo ejemplos aislados. Esto debilita mucho el impacto |
| 3 | Impacto | La tabla describe los mecanismos correctamente pero no demuestra su magnitud. Una columna con "N de eventos registrados" transformaría la tabla |
| 4 | Errata | "Pode Legislativo" en la fila de CLPI (falta una 'r') |

#### `cap1_03_ejemplos_paradigmaticos.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Dato | Concesiones: "32 menciones" — ¿cuántos eventos distintos representan? ¿cuántos proyectos involucran? |
| 2 | Dato | Peñasquito: datos fuertes (412 concesiones, 89,000+ ha, vigencia hasta 2058). Bien documentado con fuente de Secretaría de Economía. Este es el tipo de dato contundente que necesitan más |
| 3 | Dato | Decretos: "12 menciones" — nuevamente, ¿cuántos decretos distintos? |
| 4 | Dato | Asambleas apócrifas: solo 2 ejemplos (Tren Maya y CIIT). ¿Es porque solo hay 2 o porque solo esos fueron cubiertos por la prensa? La respuesta cambia la interpretación |
| 5 | Dato | Donaciones GN: los autores reconocen que "los casos son mínimos en comparación". Aun así se incluye una sección completa. ¿Vale la pena mantenerla o debilita la percepción general? |
| 6 | Impacto | Los patrones identificados en concesiones mineras (filiales, prestanombres, periodos largos) son un hallazgo valioso que podría reforzarse con datos de la base OCSA |
| 7 | Fuente | "Trey Maya" — errata, debería ser "Tren Maya" |

#### `cap1_04_reflexiones_anexo_fuentes.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Impacto | Las reflexiones son correctas pero genéricas. No recapitulan los hallazgos cuantitativos del capítulo |
| 2 | Fuente | Bibliografía completa y bien formateada. ~40 fuentes. Adecuada |

---

### Capítulo 2 — Mecanismos Institucionales de Despojo (MID)

#### `cap2_01_introduccion_definicion_MID.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Concepto | La distinción MLD/MID es clara y bien fundamentada teóricamente. Punto fuerte de la investigación |
| 2 | Concepto | Las 5 características de los MID están bien articuladas. El marco es sólido |
| 3 | Marcas | Quedan varias marcas `[.mark]` en el texto que parecen anotaciones internas no eliminadas |

#### `cap2_02_consultas_CLPI.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Dato | "86 de los 1,170 proyectos revisados" — primera vez que aparece el universo total (1,170 proyectos). Este denominador debería mencionarse desde cap1_01 |
| 2 | Dato | Los datos de la ASF son el punto más fuerte de toda la investigación: 222 solicitudes, solo 21 procedentes (9.4%), 173 improcedentes (77.9%). Esto es demoledor y verificable con fuente oficial |
| 3 | Dato | 222 - 21 - 173 = 28 solicitudes sin clasificar en procedente/improcedente. La tabla muestra que son los 28 casos donde se emitió informe de existencia de comunidades. ¿Qué pasó con esos 28? ¿Están en proceso? |
| 4 | Impacto | La Gráfica 1 (proyectos con CLPI) usa porcentajes de menciones, no de eventos. Mismo problema transversal |
| 5 | Incompleto | Línea 98: "[Aquí me falta un esquema con actores involucrados]" — falta contenido |
| 6 | Dato | "173 menciones equivalentes al 58.8% del total de eventos documentados (294)" — aquí se introduce otro denominador (294 eventos). ¿De dónde sale? ¿Es distinto de los 702 o de los 1,170? Confuso |
| 7 | Impacto | La solicitud de información al INPI (340009700003926) es un recurso propio valioso. ¿Llegó la respuesta completa? El texto parece truncado |

#### `cap2_03_irregularidades_consultas.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Estructura | Las 5 irregularidades están bien documentadas con casos concretos. Sección sólida |
| 2 | Dato | Cada irregularidad tiene 1-2 ejemplos pero sin dato cuantitativo: ¿cuántas veces se documentó cada tipo? |
| 3 | Impacto | El caso de fragmentación del PIM es fuerte: "63% de los consultados no pertenecían a regiones directamente afectadas". Este tipo de dato concreto es lo que hace falta en otras secciones |

#### `cap2_04_instrumentos_evaluacion_impacto.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Dato | "El promedio general de menciones de omisión en todos los proyectos se sitúa en 1.67%" — ¿1.67% de qué? ¿Del total de menciones del proyecto? ¿Del total general? El denominador no es claro |
| 2 | Estructura | La Tabla 3 (instrumentos de evaluación) es excelente: bien estructurada, con fundamento legal, alcance y autoridad. Punto fuerte |
| 3 | Estructura | Las 3 irregularidades (captura técnica, contradicciones, incumplimientos tolerados) están bien documentadas |
| 4 | Dato | El caso de Perfect Day/Mahahual es reciente (2026) y relevante. Pero se basa en análisis de Greenpeace, no propio |
| 5 | Impacto | Sección 2.2.1 es muy descriptiva (explica qué es cada instrumento) pero le falta peso analítico. ¿Cuántas MIA fueron cuestionadas? ¿Cuántas ERA se omitieron? |

#### `cap2_05_reflexiones_fuentes.md` — REVISADO

| # | Tipo | Observación |
|---|------|-------------|
| 1 | Impacto | Las reflexiones son más fuertes que las del Cap. 1 porque recuperan hallazgos concretos (datos ASF, fragmentación institucional) |
| 2 | Fuente | Bibliografía completa. ~30 fuentes. Adecuada |

---

## Resumen de problemas recurrentes

### Datos e impacto

| Problema | Frecuencia | Prioridad |
|----------|-----------|-----------|
| Unidad de medida (menciones vs eventos) | Toda la investigación | ALTA |
| Porcentajes sin denominador claro | cap1_01, cap2_02, cap2_04 | ALTA |
| Inconsistencia numérica (18 vs 12 mecanismos) | cap1_01 vs cap1_02 | ALTA |
| Gráficas como imágenes sin datos tabulados | Todos los capítulos | MEDIA |
| Ejemplos aislados sin contexto cuantitativo | cap1_02, cap1_03, cap2_03 | MEDIA |
| Datos fuertes presentados sin énfasis | cap1_01 (MIA 148/5), cap2_02 (ASF) | MEDIA |

### Oportunidades de mejora con la base OCSA

| Oportunidad | Secciones que beneficia |
|-------------|------------------------|
| Reemplazar "menciones" por eventos únicos como unidad | Toda la investigación |
| Agregar conteos por tipo de mecanismo a la Tabla 1 | cap1_02 |
| Cruzar mecanismos con tipos de proyecto extractivo | cap1_01, cap1_03 |
| Vincular mecanismos de despojo con impactos documentados | cap1_03, cap2_04 |
| Georreferenciar los mecanismos (mapa por estado) | Capítulos 1 y 2 |
| Análisis temporal: ¿los mecanismos aumentan? | cap1_01 |

### Forma y completitud

| Problema | Ubicación |
|----------|-----------|
| Contenido faltante ("me falta un esquema") | cap2_02, línea 98 |
| Marcas `[.mark]` no eliminadas | cap2_01, cap2_02 |
| Erratas ("Pode Legislativo", "Trey Maya") | cap1_02, cap1_03 |
| Texto truncado (respuesta INPI) | cap2_02 |

---

## Registro de sesiones de revisión

| Fecha | Alcance | Participantes | Notas |
|-------|---------|---------------|-------|
| 2026-04-05 | Lectura completa y primera revisión | Ricardo + Claude | Documento inicial de seguimiento |
| | | | |