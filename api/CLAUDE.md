## Project Overview

Django REST API for the **Observatorio de Conflictos Socioambientales (OCSA)**, managing data about socio-environmental conflicts, mega-projects, actors, impacts, and events in Mexico from 2017 to present. Based on newspaper articles (Jornada, Reforma y Proceso).

## Code Style Rules

- Add **docstrings** to all views, serializers, and complex functions
  (type hints are already required globally).
- Avoid boilerplate and repetition by leveraging DRF's generic views,
  mixins, and the `BaseViewSet` where possible. If the standard suggests
  it, answer before choosing the best approach for the specific case.
- Never execute `makemigrations` or `migrate` commands yourself. I will
  execute them manually after reviewing changes.
## Common Commands


## Architecture

### Domain-Driven Structure

Each major domain is a standalone Django app:

| App | Purpose |
|-----|---------|
| `source/` | Notes/articles scraped or manually entered |
| `project/` | Mega-projects and socio-environmental conflicts |
| `actor/` | People and organizations involved |
| `event/` | Events related to conflicts/projects |
| `impact/` | Impact records |
| `df/` | Forced displacement (desplazamiento forzado) |
| `classify/` | Shared catalogs/taxonomies (participant types, sectors, interests, etc.) |
| `space_time/` | Geographic data (states, municipalities, localities) |
| `work_flux/` | Cross-cutting status and workflow control |
| `profile_auth/` | Custom `User` model with `is_full_editor` / `is_admin` roles |
| `task/` | Async task management |
| `api/` | REST endpoints — views organized by domain in `api/views/` |

There are three grops of events:
violence against activists, collective actions and legal resources (against and in favor of projects)

There are two groups of impacts:
Social and environmental impacts.

### API Layer (`api/`)

All ViewSets are registered in `api/urls.py` under `/api/`. The main router exposes standard CRUD plus custom actions. Views are organized as subpackages: `api/views/note/`, `api/views/project/`, etc.

### Key base classes (api/views/common_views.py)
- `BaseViewSet` — extends `ModelViewSet` with `CustomPagination`, `UnaccentSearchFilter`, `DjangoFilterBackend`, `OrderingFilter`, and a custom delete confirmation mixin.
- `UnaccentSearchFilter` — uses `unaccent__icontains` lookup for accent-insensitive search (PostgreSQL only; falls back gracefully on SQLite).
- `AdvancedConditionalFieldsViewMixin` — excludes serializer fields based on `field_permissions` dict keyed by role (`anonymous`, `authenticated`, `staff`).

### Creating new Views
- **APIView vs ViewSet**: Use `views.APIView` for non-model or custom
  auth endpoints (login, recovery, etc.). Use `BaseViewSet` /
  `BaseGenericViewSet` (from `api/views/common_views.py`) for standard
  model CRUD.
- **Request validation**: Always validate `request.data` through a DRF
  serializer — never access it directly via `.get()`. Use
  `serializer.is_valid(raise_exception=True)` so DRF handles the 400
  response automatically.
- **Error response format**:
  - Field errors (auto via `raise_exception=True`): serializer errors
    dict returned directly → HTTP 400
  - Single non-field message: `{'detail': '...'}` → appropriate status
- **Serializer location**: Place serializers for a given sub-package in
  `api/views/{sub-package}/serializers.py`
  (e.g., auth views → `api/views/auth/serializers.py`).
- Import the serializers and common elements at the beginning of the
  file, and then define the views.
### QuerySet optimization for nested serializers
Every time a View or its related Serializers are created or modified,
follow this checklist to prevent N+1 queries:

1. **Inspect serializer fields for relations.** Check every serializer
   referenced in `action_serializers` (list, create, retrieve, update,
   etc.). Identify fields that traverse relationships — nested
   serializers, `source="rel.field"` declarations,
   `SerializerMethodField`s that access related objects, and any
   `StringRelatedField` or `SlugRelatedField` pointing to a FK/M2M.

2. **Ensure the base `queryset` covers the common case.** Add
   `select_related()` for ForeignKey / OneToOne lookups and
   `prefetch_related()` for reverse FKs / ManyToMany lookups that are
   shared by most or all actions. This is the default defined at the
   class level (`queryset = Model.objects.select_related(...)`).

3. **Decide whether to override `get_queryset()` per action.**
   - **Override when** different actions have significantly different
     nesting depth. For example, `retrieve` may use a deeply nested
     serializer (multi-level joins) while `list` only needs shallow
     fields. Keeping the heavy prefetches on every action wastes
     database work. In that case, override `get_queryset()` and branch
     on `self.action`:
     ```python
     def get_queryset(self):
         qs = super().get_queryset()  # base queryset
         if self.action == 'retrieve':
             qs = qs.prefetch_related(
                 'deep_relation__nested_relation',
             )
         return qs
     ```
   - **Do not override when** the difference is minor — e.g., only one
     action uses a single extra shallow prefetch that the others
     ignore. In that case, just include it in the base `queryset`.
     A small unused prefetch is cheaper than the added complexity of
     a branched `get_queryset()`.

4. **Rule of thumb for the threshold.** If the extra prefetch adds a
   new join level (nested `Prefetch` objects, or chained double-
   underscore paths like `a__b__c`) and is only needed by one action,
   override `get_queryset()`. If it is a single flat
   `prefetch_related('simple_rel')`, keep it in the base `queryset`.

### Permissions

Custom permission classes in `profile_auth/` (and referenced in `core/settings/`):
- `IsFullEditorOrReadOnly` — default; full editors can write, others read-only
- `ByStatusOrReadOnly` — editing gated by record status
- `IsEditorOrCreateOrRead` — allows creation with validation
- `DynamicCatalogPermission` — for catalog endpoints
- `LocationPermission` — for geographic data

### Settings

`core/settings/__init__.py` — single settings file.

### Database

- **PostgreSQL** with `unaccent` extension
- `AUTH_USER_MODEL = "profile_auth.User"`

### External Integrations

- **OpenAI / Google Generative AI**: AI-assisted record pre-classification and pre-recording based on article content
- **BeautifulSoup / lxml**: news scraping from multiple sources
- **openpyxl / yeekooxlsx_export**: Excel exports

