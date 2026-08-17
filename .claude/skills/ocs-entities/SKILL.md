---
name: ocs-entities
description: Referencia de entidades OCSA (proyecto, actor, participación, mención, evento, impacto, desplazamiento, ubicación) y sus relaciones. Activar al construir queries, filtros, exportaciones o consultar campos/catálogos que crucen estas entidades. Mention es el hub central que conecta Note, Project, Participant/Actor, Event, Impact y StatusHistory.
---

# OCS Entities — Reference Index

Cada entidad tiene su propio archivo en `references/`. Cárgalos bajo demanda según lo que se esté trabajando:

| Entidad | Archivo | Cuándo cargarlo |
|---------|---------|---------------------------------------|
| Megaproyecto / Estatus | [project.md](references/project.md) | Modelos `Project`, `Conflict`, `StatusHistory`, tipos de proyecto, catálogos de estatus |
| Actor / Participante | [actor.md](references/actor.md) | Modelos `Actor`, `Participant`, sector, pertenencias, intereses |
| Afectación | [impact.md](references/impact.md) | Modelos `Impact`, tipos de impacto (ecológico o social) , desplazamiento |
| Evento | [event.md](references/event.md) | Modelos `Event`, Grupos de evento (violencias, acciones colectivas y mecanismos legales), roles de involucramiento y propósitos del mecanismo |
| Desplazamiento forzado | [displacement.md](references/displacement.md) | Módulo `api/df/`, modelo `Displacement` y sus catálogos |
| Ubicación | [location.md](references/location.md) | Modelo `Location`, contrato de `geojson` (punto/línea/polígono, Multi*), filtros «tiene geometría» y de completitud, importación de archivos |


> Para el ciclo de vida de `Article → Note → Mention` y el pipeline de pre-captura IA, ver `api/source/CLAUDE.md`.**
