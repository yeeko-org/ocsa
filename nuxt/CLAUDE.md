# nuxt/ — front end

Nuxt 3 + Vuetify 4, Pinia for state, consuming the Django API in `api/`. Domain, structure and commit convention: [../CLAUDE.md](../CLAUDE.md). Paths below are relative to `nuxt/`.

## Commands

Package manager is pnpm (`packageManager` in `package.json`; the lockfile is gitignored) — never `npm i`.

- `pnpm test` — Vitest, pinned to 3.x on purpose: vite 5 rejects vitest 4.
- `pnpm build` — the only static check there is; no lint script.

## Architecture

### API & Auth
- `plugins/api.ts` — creates an axios instance (`$api`) with base URL from `NUXT_API_URL` (client-side under `ocsa.ibero.mx` it switches to the relative `/api-ocsa`, the Ibero nginx same-origin proxy); auto-injects token from `auth_ocsa` cookie via request interceptor.
- `store/auth.js` — token lives in `auth_ocsa` cookie, 24-hour TTL. Roles: `is_staff`, `is_full_editor`, `is_mini_editor`.
- `middleware/dashboard.js` — protects all `/dashboard/*` routes: checks auth, fetches catalogs on first load, sets active collection from route params.

### State (Pinia)
- `store/index.js` — the main store. Holds catalogs (`cats`), all loaded records (`all_nodes`), schemas, and filter state. All CRUD API calls go here (`fetchCatalogs`, `fetchElements`, `saveSimple`, `patchSimple`, `deleteSimple`). Uses axios CancelToken to cancel in-flight list requests.
- `store/dash.js` — global UI state. `showSnackbar(message, color = 'success')` is the only way to raise a toast; always take it from `useDashboardStore`, not the main store.
- `store/geo.js` — geographic hierarchy (states → municipalities → localities), uses Composition API setup() pattern unlike the other Options API stores.

### Collections & Filters
Each data domain is a "collection" (e.g. `actores`, `proyectos`, `eventos`). Catalogs have filter groups with hierarchical categories built via D3 `stratify()` in `composables/nodes.js`. `calculateNewCats()` rebuilds the tree after any catalog mutation. `composables/fetch.js` manages debounced (600 ms) list fetching with global `results`, `loading_fetch`, `final_filters` refs.

### Component Conventions
- Files named `{Model}{Header|Sheet|Edit|EditSimple|Card}.vue` under `components/dashboard/{app_label}/{snake_name}/` are loaded by name convention, with the path built at runtime: **nothing imports them, and that is normal**.
- **Warning**: a grep with zero importers on those files does NOT mean dead code. Never rename, move, delete or refactor them without reading the skill first.
- All the detail (suffixes, resolvers, fallbacks, props, emits, filters, massive edit, CRUD contract) lives in the `dashboard-collections` skill.
- CRUD is entirely dialog-driven: `DialogEdit`, `DialogDelete`, `DialogSearch`.
- Mix of Options API (older) and `<script setup>` (preferred for new code).

### Maps
Mapbox GL (`mapbox-gl` + `@mapbox/mapbox-gl-draw`) used in `pages/mapa.vue` and `components/map/`.
- Location editor: `composables/useLocationDraw.js` owns the map and the draw control for `components/dashboard/space_time/location/LocationMapCard.vue`; per-type `draw_mode` and `draw_icon` live in `composables/location_types.js`. Drawing only starts from the explicit "Agregar…" button, and the composable calls `map.remove()` on unmount — every leaked map holds a WebGL context.
- Public map cache: the facets/actors index is served from Redis. `projectFacets` and `mapActors` in `store/index.js` early-return once loaded, so `rebuildMapIndex()` (staff-only "Recargar mapa" button in `layouts/dashboard.vue`, `POST map/index/rebuild/`) must null both out or the rebuilt index stays invisible until a page reload.

### Content & Copyright
- Notes carry copyrighted source text — never render `paragraphs` / article body in `components/map/` or any public-facing view. Only metadata (title, date, source) is allowed.