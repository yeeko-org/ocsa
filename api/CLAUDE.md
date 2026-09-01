# api/ — Django REST API

Django + DRF back end of the OCSA monorepo. Domain, structure and commit convention: [../CLAUDE.md](../CLAUDE.md). Paths below are relative to `api/`.

## Architecture

### Non-obvious Django Apps

| App | Purpose |
|-----|---------|
| `source/` | Notes/articles scraped or manually entered |
| `df/` | Forced displacement (desplazamiento forzado) |
| `classify/` | Shared catalogs/taxonomies (participant types, sectors, interests) |
| `space_time/` | Geographic data (states, municipalities, localities, `Location` with its `geojson` contract in `space_time/geometry.py`) |
| `work_flux/` | Cross-cutting status and workflow control |
| `profile_auth/` | Custom `User` model with `is_full_editor` / `is_admin` roles |
| `ocsa_legacy/` + `*/migrate/`, `migrate_*` commands | Bridge to the pre-rewrite system: unmanaged models over PostgreSQL schema `ocs` and one-off data migrations, already run. Not part of daily operation — see docs `2026-08-17-plataforma-legacy-y-migracion` |

### API Layer (`api/`)

All ViewSets registered in `api/urls.py`. Views organized as subpackages: `api/views/note/`, `api/views/project/`, etc. Serializers go in `api/views/{sub-package}/serializers.py`. Import serializers and common elements at the top of each view file.

`api/` is **not** in `INSTALLED_APPS` — it's a views/urls/serializers package only. Put management commands in a registered app (`work_flux/management/commands/`). Importable logic can still live under `api/`.

Public-map visibility has a single source: `api/views/map/visibility.py` (`visible_locations` / `visible_projects` / `visible_mentions`, docs `adr-0022`). Every map endpoint consumes it; never re-implement the condition inline — that is what produced ghost pins.

### Key Base Classes (`api/views/common_views.py`)
- `BaseViewSet` — extends `ModelViewSet` with `CustomPagination`, `UnaccentSearchFilter`, `DjangoFilterBackend`, `OrderingFilter`, and a delete confirmation mixin.
- `UnaccentSearchFilter` — uses `unaccent__icontains` for accent-insensitive search (PostgreSQL only; falls back on SQLite).
- `AdvancedConditionalFieldsViewMixin` — excludes serializer fields based on `field_permissions` dict keyed by role (`anonymous`, `authenticated`, `staff`).

### Permissions (`profile_auth/`)
- `IsFullEditorOrReadOnly` — default; full editors can write, others read-only
- `ByStatusOrReadOnly` — editing gated by record status
- `IsEditorOrCreateOrRead` — allows creation with validation
- `DynamicCatalogPermission` — for catalog endpoints
- `LocationPermission` — for geographic data

### Catalog/Collection Registry
Register a ViewSet in `catalog_registry`/`collection_registry` only when the model is a catalog of options (`category_*`) or a main collection entity (`primary/secondary/relational`). Cross-cutting/infrastructure ViewSets (e.g. `StatusControl`, `InvolvedRole`) stay as manual registrations, even if trivial — they have distinct semantics. See the `manage-collections` skill.

### Settings & Database
- Settings: `core/settings/__init__.py` (single file)
- PostgreSQL with `unaccent` extension; `AUTH_USER_MODEL = "profile_auth.User"`
- The local DB is a restored copy of production (RDS, not the EC2). Procedure and freshness check: docs `2026-08-26-copia-de-produccion-a-local`
- `migrate_initial_data` only creates the `StatusControl` rows that are missing; existing rows are never touched — the admin is the living source of `order`/`color`/`icon`/`priority` (docs `task-86`)

### External Integrations
- **OpenAI / Google Generative AI**: AI-assisted record pre-classification
- **BeautifulSoup / lxml**: news scraping from multiple sources
- **openpyxl / yeekooxlsx_export**: Excel exports
- **Redis**: caches the public map's facets/actors index (db 1 in production). Rebuilt by `rebuild_map_index` (06:00 UTC cron) or on demand via `POST map/index/rebuild/`; nothing else expires it
- **S3 (django-storages)**: `NoteFile`/`ProjectFile` files in production (`USE_S3_FILES=1`, class `INTELLIGENT_TIERING`, public read via bucket policy on `data_files/*`); local dev keeps disk storage. Storage per field via `core/storages.py::select_docs_storage`

### Geographic data (INEGI)
- Cartography (state, municipal and locality polygons) and the AGEEML catalogs are not versioned (>270 MB): `space_time/geo_files/download_inegi.sh` fetches them — [cartografia.md](../.claude/skills/ocs-geo/references/cartografia.md) (skill `ocs-geo`).
- Load order: `load_states_data`, `load_municipios`, `load_localidades`, `load_geometries`; the last three are idempotent with `--dry-run` and no loader ever deletes (`Locality.is_current` marks retired rows).
- No PostGIS: `space_time/geolocate.py` computes with shapely in memory, and polygons live in 1:1 `*Geometry` models (WKB EPSG:6372, simplified) so `__all__` serializers of `State`/`Municipality` never carry them.
- Rules, thresholds and invariants of the engine: skill `ocs-geo` (`.claude/skills/ocs-geo/`) and docs `adr-0026`.

### Testing
Suites unitarias con el runner nativo (`manage.py test source` y `manage.py test space_time`) más diagnósticos re-ejecutables que golpean servicios reales (proxy, PressReader, Gemini) y por tanto cuestan. Ver [TESTING.md](TESTING.md) antes de correr cualquiera.

### Documentación de proceso
Decisiones (ADR), tareas abiertas y bitácoras viven en el submódulo privado `../docs/`, indexadas por frontmatter y enlazadas con `[[id]]`. Ver el skill `documenter`.