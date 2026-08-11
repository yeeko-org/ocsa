# nuxt/ — front end

Nuxt 3 + Vuetify 4, Pinia for state, consuming the Django API in `api/`. Domain, structure and commit convention: [../CLAUDE.md](../CLAUDE.md). Paths below are relative to `nuxt/`.

## Architecture

### API & Auth
- `plugins/api.ts` — creates an axios instance (`$api`) with base URL from `NUXT_API_URL`; auto-injects token from `auth_ocsa` cookie via request interceptor.
- `store/auth.js` — token lives in `auth_ocsa` cookie, 24-hour TTL. Roles: `is_staff`, `is_full_editor`, `is_mini_editor`.
- `middleware/dashboard.js` — protects all `/dashboard/*` routes: checks auth, fetches catalogs on first load, sets active collection from route params.

### State (Pinia)
- `store/index.js` — the main store. Holds catalogs (`cats`), all loaded records (`all_nodes`), schemas, and filter state. All CRUD API calls go here (`fetchCatalogs`, `fetchElements`, `saveSimple`, `patchSimple`, `deleteSimple`). Uses axios CancelToken to cancel in-flight list requests.
- `store/dash.js` — global UI state (`showSnackbar`).
- `store/geo.js` — geographic hierarchy (states → municipalities → localities), uses Composition API setup() pattern unlike the other Options API stores.

### Collections & Filters
Each data domain is a "collection" (e.g. `actores`, `proyectos`, `eventos`). Catalogs have filter groups with hierarchical categories built via D3 `stratify()` in `composables/nodes.js`. `calculateNewCats()` rebuilds the tree after any catalog mutation. `composables/fetch.js` manages debounced (600 ms) list fetching with global `results`, `loading_fetch`, `final_filters` refs.

### Component Conventions
- CRUD is entirely dialog-driven: `DialogEdit`, `DialogDelete`, `DialogSearch`.
- Reusable shells: `components/dashboard/common/generic/` — `CardCommon`, `EditCommon`, `HeaderCommon`. Domain components slot into these.
- Standard props on edit components: `full_main` (the model object), `collection_data`, `collection_name`, `is_edit`, `is_massive_edit`.
- Standard emits: `item-saved`, `item-deleted`.
- Massive edit mode (`is_massive_edit`) hits a different endpoint (`massive_patch/`).
- Mix of Options API (older) and `<script setup>` (preferred for new code).

### Maps
Mapbox GL (`mapbox-gl` + `@mapbox/mapbox-gl-draw`) used in `pages/mapa.vue` and `components/map/`.

### Content & Copyright
- Notes carry copyrighted source text — never render `paragraphs` / article body in `components/map/` or any public-facing view. Only metadata (title, date, source) is allowed.