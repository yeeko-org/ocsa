## Project Overview

Django REST API for the **Observatorio de Conflictos Socioambientales (OCSA)**, managing data about socio-environmental conflicts, mega-projects, actors, impacts, and events in Mexico from 2017 to present. Based on newspaper articles (Jornada, Reforma y Proceso).

## Architecture

### Non-obvious Django Apps

| App | Purpose |
|-----|---------|
| `source/` | Notes/articles scraped or manually entered |
| `df/` | Forced displacement (desplazamiento forzado) |
| `classify/` | Shared catalogs/taxonomies (participant types, sectors, interests) |
| `space_time/` | Geographic data (states, municipalities, localities) |
| `work_flux/` | Cross-cutting status and workflow control |
| `profile_auth/` | Custom `User` model with `is_full_editor` / `is_admin` roles |

Event types: violence against activists · collective actions · legal resources (against/in favor of projects)
Impact types: social · environmental

### API Layer (`api/`)

All ViewSets registered in `api/urls.py`. Views organized as subpackages: `api/views/note/`, `api/views/project/`, etc. Serializers go in `api/views/{sub-package}/serializers.py`. Import serializers and common elements at the top of each view file.

`api/` is **not** in `INSTALLED_APPS` — it's a views/urls/serializers package only. Put management commands in a registered app (`work_flux/management/commands/`). Importable logic can still live under `api/`.

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

### External Integrations
- **OpenAI / Google Generative AI**: AI-assisted record pre-classification
- **BeautifulSoup / lxml**: news scraping from multiple sources
- **openpyxl / yeekooxlsx_export**: Excel exports
- **S3 (django-storages)**: `NoteFile`/`ProjectFile` files in production
  (`USE_S3_FILES=1`, class `INTELLIGENT_TIERING`, public read via bucket
  policy on `data_files/*`); local dev keeps disk storage. Storage per
  field via `core/storages.py::select_docs_storage`

### Testing
No hay suite montada; lo que existe son diagnósticos re-ejecutables que
golpean servicios reales (proxy, PressReader, Gemini) y por tanto cuestan.
Ver [TESTING.md](TESTING.md) antes de correr cualquiera.

### Documentación de proceso
Decisiones (ADR), tareas abiertas y bitácoras viven en `docs/`, indexadas
por frontmatter y enlazadas con `[[id]]`. Ver el skill `documenter`.