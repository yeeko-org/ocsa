---
name: xls-export-blocks
description: XLSX export pattern. Use when adding, modifying, or debugging Excel exports.
---

# Exportaciones XLSX — yeeko_xlsx_export v2.0

Paquete: `D:\dev\open\xlsx_django_export` (yeeko_xlsx_export).
Exports del proyecto: `api/api/export_blocks/`.

---

## Conceptos clave

| Clase | Rol | Ubicacion |
|-------|-----|-----------|
| `XlsColumn` | Una columna del Excel ligada a un campo del modelo | Paquete |
| `FkColumn` | Columna que cruza una FK (hace explicito el salto) | Paquete |
| `CollectColumn` | Recolecta valores por M2M o reverse FK | Paquete |
| `Include` | Integra un bloque reutilizable dentro de otro export | Paquete |
| `ModelExport` | Clase base: define columnas, modelo, y logica de exportacion | Paquete |
| `ExportActionMixin` | Mixin que agrega `@action export_xls` a un ViewSet | Paquete |
| `ExportView` | Vista standalone para urlpatterns (alternativa al mixin) | Paquete |

Imports:
```python
from yeeko_xlsx_export import (
    CollectColumn, FkColumn, Include, ModelExport, XlsColumn,
    ExportActionMixin,  # para ViewSets
    ExportView,         # para vistas standalone
)
```

---

## Crear un export nuevo

### 1. Definir la clase

```python
# api/api/export_blocks/my_entity.py
from my_app.models import MyEntity
from yeeko_xlsx_export import ModelExport, XlsColumn, FkColumn, Include
from api.export_blocks.conditions import is_authenticated

class MyEntityExport(ModelExport):
    model = MyEntity
    export_name = "Exportacion de entidades"
    columns = [
        XlsColumn("id"),
        XlsColumn("name", width=35),
        FkColumn("category", "name", title="Categoria"),
        XlsColumn(
            "secret_field",
            condition=is_authenticated,
        ),
        Include(SomeReusableBlock, through="relation"),
    ]
```

### 2. Registrar en CollectionSchema

```python
# api/my_app/catalog_schema.py
from api.export_blocks.my_entity import MyEntityExport

@collection_registry.register
class MyEntitySchema(CollectionSchema):
    model = MyEntity
    viewset_class = MyEntityViewSet
    xls_export_class = MyEntityExport  # auto-registra /export_xls/
```

El registry inyecta `ExportActionMixin` al ViewSet
automaticamente, creando el endpoint
`GET /api/my_entity/export_xls/`. El ViewSet NO necesita heredar
de ningun mixin de exportacion.

Los filtros del ViewSet (filterset_class, search_fields,
ordering) se aplican automaticamente al export.

### 3. Listo

No se necesita:
- `select_related` / `prefetch_related` manual (se infiere)
- `extract()` manual (se auto-genera)
- `xls_attrs`, `xls_name`, `get_export_rows()` en el ViewSet

---

## XlsColumn — referencia rapida

```python
XlsColumn(
    field,                    # nombre del campo o key logica
    *,
    title=None,               # header (default: verbose_name)
    width=None,               # ancho (default: segun tipo)
    condition=None,           # Callable(request) -> bool
    operation=None,           # post-procesamiento del valor
    source=None,              # ruta ORM alternativa
    join_separator=", ",      # separador para operation="join"
)
```

### Auto-resolucion de title

| Caso | Resultado |
|------|-----------|
| `title` proporcionado | Se usa tal cual |
| Campo `name` | `"Nombre de {model.verbose_name}"` |
| Campo `id` | `"ID de {model.verbose_name}"` |
| Campo con `verbose_name` | Se capitaliza |
| Fallback | `field_name` humanizado |

No repetir `title` cuando el default ya es correcto.

### Auto-resolucion de width

| Tipo de campo Django | Width |
|---------------------|-------|
| PK (AutoField, etc.) | 5 |
| BooleanField | 6 |
| IntegerField / SmallInt | 8 |
| DateField | 12 |
| DateTimeField | 15 |
| CharField (max_length <= 50) | 20 |
| CharField (max_length > 50) | 30 |
| TextField | 35 |
| ForeignKey | 25 |
| Campo virtual / fallback | 15 |

No repetir `width` cuando el default ya es correcto.

### `source` — ruta ORM alternativa

Cuando el valor se obtiene por un path FK distinto al `field`:

```python
# field = key en el dict de fila
# source = path real para extraer el valor via FK
FkColumn(
    "status_validation", "public_name",
    title="Status de validación",
)
```

**No usar `source` + `operation` en XlsColumn.** Para relaciones
M2M o reverse FK, usar `CollectColumn` (ver seccion dedicada).

### Operations

Se aplican sobre el valor extraido antes de escribir en celda.

| Operation | Entrada | Salida |
|-----------|---------|--------|
| `count` | iterable | `len(value)` |
| `sum` | iterable numerico | `sum(value)` |
| `min` | iterable comparable | menor valor |
| `max` | iterable comparable | mayor valor |
| `first` | iterable | primer elemento |
| `last` | iterable | ultimo elemento |
| `join` | iterable de strings | `sep.join(value)` |
| `distinct_count` | iterable | `len(set(value))` |

Las operations se usan principalmente con `CollectColumn`.

### Conditions

Callables que reciben `request` y retornan `bool`:

```python
from api.export_blocks.conditions import is_authenticated

XlsColumn("secret", condition=is_authenticated)
```

Definir nuevas conditions en `api/api/export_blocks/conditions.py`.

---

## FkColumn — FK explicita

```python
FkColumn(relation, field, **kwargs)
```

Hace explicito el salto de FK. Permite auto-inferir
`select_related`.

```python
# Equivalentes, pero FkColumn es mas claro:
XlsColumn("impact_type__impact_group__name")
FkColumn("impact_type", "impact_group__name")
```

Usar FkColumn cuando el primer segmento es una FK directa del
modelo. Usar XlsColumn para campos propios, anotaciones o paths
via `source`.

---

## CollectColumn — M2M y reverse FK

```python
CollectColumn(relation, field, **kwargs)
```

Para relaciones donde hay **multiples objetos** al otro lado:
M2M, reverse FK, o cadenas profundas que cruzan alguna de estas.

```python
# M2M simple — default operation="join"
CollectColumn(
    "belongs", "name",
    title="Pertenencias",
)

# Cadena profunda con operacion distinta
CollectColumn(
    "participants__mention__note", "date",
    title="Numero de notas",
    operation="count",
)

# Otra operacion sobre la misma cadena
CollectColumn(
    "mentions__note", "date",
    title="Primera nota",
    operation="min",
)
```

### Diferencias con FkColumn

| | FkColumn | CollectColumn |
|--|----------|---------------|
| Relacion | FK / OneToOne (1:1, N:1) | M2M / reverse FK (1:N, N:M) |
| ORM | `select_related` | `prefetch_related` |
| `needs_collect` | False | True (siempre) |
| `operation` default | None | `"join"` |

### Regla de eleccion

- Campo propio del modelo → `XlsColumn`
- FK directa → `FkColumn`
- M2M o reverse FK → `CollectColumn`

---

## Include — composicion de bloques

```python
Include(block_class, through=None)
```

### Con `through` (sub-objeto via relacion)

```python
Include(MentionBlock, through="mention")
```

El framework hace `obj.mention` para obtener el sub-objeto y
luego extrae las columnas del bloque desde ahi. Las keys del
dict se prefijan automaticamente: `mention__note__id`, etc.

Infiere `select_related` o `prefetch_related` segun el tipo de
relacion.

### Sin `through` (campos directos)

```python
Include(ActorBlock)
```

Los campos del bloque se leen directamente del objeto raiz.
Util para componer bloques reutilizables sin cambio de contexto.

---

## Bloques reutilizables

Un bloque es un `ModelExport` sin `export_name`, pensado para
incluirse via `Include`:

```python
class NoteBlock(ModelExport):
    model = Note
    columns = [
        XlsColumn("id"),
        XlsColumn("date"),
        XlsColumn("title", width=40),
        FkColumn("source", "name", title="Medio"),
    ]
```

Se usa asi:

```python
class ImpactExport(ModelExport):
    model = Impact
    columns = [
        XlsColumn("id"),
        Include(NoteBlock, through="mention__note"),
    ]
```

---

## Overrides disponibles en ModelExport

```python
class MyExport(ModelExport):
    model = MyModel
    export_name = "Mi exportacion"
    columns = [...]
    extra_prefetch = []       # prefetches no inferibles

    def get_base_queryset(self) -> QuerySet:
        """Default: model.objects.all()"""

    def get_annotations(self) -> dict:
        """Anotaciones ORM (Subquery, Count, etc). Default: {}"""

    def extract_row(self, obj, request) -> dict | list[dict]:
        """Override solo para logica compleja.
        Retornar list[dict] para expansion 1->N."""

    def post_process_rows(self, rows) -> list[dict]:
        """Hook post-extraccion. Default: identidad."""
```

### Expansion 1->N

Cuando un objeto produce multiples filas (ej. Participant con
N involvements), `extract_row` retorna `list[dict]`:

```python
def extract_row(self, obj, request):
    base = super().extract_row(obj, request)
    involvements = list(obj.involvements.all())
    if not involvements:
        return [base]
    return [
        {**base, "event": EventBlock().extract_row(inv.event, request)}
        for inv in involvements
    ]
```

---

## Inferencia automatica

El framework inspecciona las columnas y genera:

- **select_related**: para FKs/OneToOne detectadas en paths
- **prefetch_related**: para M2M/reverse FK detectadas en paths
- **Titulos**: desde `verbose_name` del campo Django
- **Anchos**: segun el tipo de campo Django
- **Extraccion**: `getattr` encadenado con manejo de None

Regla de optimizacion: una vez que un path cruza una frontera
de prefetch (reverse FK o M2M), todos los segmentos
subsiguientes extienden el `prefetch_related` — no se puede
volver a `select_related`.

Si la inferencia no alcanza, usar `extra_prefetch`:

```python
class ParticipantExport(ModelExport):
    extra_prefetch = [
        "involvements__event__event_type",
        "involvements__involved_role",
    ]
```

---

## Registro via CollectionSchema (mecanismo)

Cuando `xls_export_class` esta definido en un schema, el
`CollectionRegistry.register_routes()` crea dinamicamente una
subclase del ViewSet que hereda de `ExportActionMixin`:

```python
# El registry hace internamente:
type(
    "MyViewSetExport",
    (ExportActionMixin, MyViewSet),
    {"xls_export_class": MyExport},
)
```

Esto agrega la action `export_xls` sin modificar el ViewSet
original. Los filtros del ViewSet se aplican al queryset del
export.

---

## Archivos del proyecto

| Archivo | Contenido |
|---------|-----------|
| `api/api/export_blocks/conditions.py` | Conditions reutilizables (`is_authenticated`) |
| `api/api/export_blocks/actor.py` | ActorBlock, ActorExport |
| `api/api/export_blocks/mention.py` | MentionBlock, NoteBlock |
| `api/api/export_blocks/event.py` | EventBlock, EventExport |
| `api/api/export_blocks/location.py` | LocationBlock |
| `api/api/export_blocks/participant.py` | ParticipantBlock, ParticipantExport |
| `api/api/export_blocks/project.py` | ProjectMiniBlock, ConflictMiniBlock, ProjectExport |