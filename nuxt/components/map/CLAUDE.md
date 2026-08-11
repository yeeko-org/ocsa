# Map components (`components/map/`)

Full-screen public map of extractive projects: Mapbox rendering, a discoverable filter system, and a unified projects panel. Mounted by `pages/mapa.vue` (layout `map`); map-specific state lives in `store/map.js`.

## Module map

- `engine/` — Mapbox layer: sources/layers (`useLayers`), D3 donut clusters (`useClusters`), click/hover handlers (`mapInteractions`), satellite toggle (`useMapStyle` + `LayerSwitch`).
- `filters/` — generic filter machinery: rail (`FilterRail`), chip rows (`FilterChips`), pickers (`FilterPicker` + `MultiSelectMap`), URL sync (`useMapFilterUrl`), static registry (`filterRegistry.js`).
- `filters/custom/` — filters that break the generic flow: actors (`FilterActors` + `ActorSearch`) and the extractivism legend (`ExtractivismLegend`).
- `panel/` — projects panel: shell `ProjectsPanel` → `ProjectsPanelContent` → `ProjectDetail`; plus `ProjectMiniCard`, `ChildProjectsList`.
- `mentions/` — note/mention content: `NoteCard`, `NotesList`, `MentionBody`, `MentionCollectionList` (grouped events/impacts), `CategoryNotesDialog`.
- `common/` — shared atoms: `HelpTooltip`, `searchIndex.js` (MiniSearch).
- `TopControls.vue` (root) — top-left island: brand + public menu + global search.

## Convention

- **Add a filter** by adding one entry to `FILTER_REGISTRY` (`filters/filterRegistry.js`) declaring `facet` (from the facets payload) or `geoIndex` (derived from geojson). The rail, chips, URL sync, and set intersection all derive from the registry — no per-filter logic.

## Architecture

- **Client-side filtering.** Three payloads: geojson (geometry) + `/map/project_facets/` + `/map/actors/` (both lazy, after first paint). The inverted index is built in memory; filtering is `Set` intersection — OR within a group, AND between groups.
- **Single source of project visibility:** the `visibleProjectIds` getter in `store/map.js`, consumed by the map, the panel, and the counter. Do not filter projects anywhere else.
- **Search** (projects + actors) is 100% client-side via MiniSearch (`common/searchIndex.js`), with accent folding in `processTerm`.

## Gotchas

- 🚫 Never render `paragraphs` / article body in `mentions/` — the source text is copyrighted. Metadata only (title, date, source).
- Large geojson feature collections must be a `shallowRef`, not a deep `ref` (a deep ref froze the main thread ~2 min).