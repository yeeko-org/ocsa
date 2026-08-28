---
name: dashboard-collections
description: >
  [nuxt] Cómo el dashboard schema-driven renderiza cualquier colección: los componentes por modelo que se cargan por convención de nombre (Header/Sheet/Edit/EditSimple/Card) mediante import() dinámico, el contrato del payload de catálogos, la barra de filtros automática y las listas de colecciones hijas. Úsalo antes de tocar, renombrar, mover o borrar cualquier archivo bajo components/dashboard/{app_label}/{snake_name}/, al agregar la vista de una colección nueva, al depurar por qué se renderiza un fallback genérico, o al trabajar en CollectionDisplay / PanelList / PanelCommon / DialogEdit / CardComponent.
---

# dashboard-collections (frontend OCSA)

## Regla de oro (leer antes de borrar nada)

Los archivos llamados `{Model}{Header|Sheet|Edit|EditSimple|Card}.vue` que viven bajo `nuxt/components/dashboard/{app_label}/{snake_name}/` **se cargan por convención de nombre, nunca se importan**. La ruta se construye en tiempo de ejecución con `import()` a partir de `collection_data`, así que **ningún archivo del repo los menciona**.

> **Un grep sin importadores NO significa código muerto.** Es el estado normal y esperado de estos componentes. Nunca los toques —renombrar, mover, borrar, refactorizar— sin consultar este skill y confirmar contra la tabla de sufijos de §2. En agosto de 2026 se borraron `LocationHeader.vue` y `LocationSheet.vue` por «no los importa nadie»; eran los que renderizaban toda la lista de ubicaciones.

Corolario práctico: para saber si uno de estos archivos se usa, la única prueba válida es que su nombre coincida con `{model_name}{Sufijo}` de una colección registrada en el backend (`api/{app}/catalog_schema.py`) y que esté en la carpeta `{app_label}/{snake_name}` de esa colección. Si coincide, está vivo.

Los demás archivos de esas mismas carpetas (`LocationMapCard.vue`, `EventToolbar.vue`, `ProjectsCriteria.vue`, …) **sí** se importan explícitamente y sí admiten el análisis normal de referencias.

## 1. De dónde sale todo

```
middleware/dashboard.js → store.fetchCatalogs()
  GET /catalogs/all/ → data
    ├─ calculateSchemas(data)   composables/cats.js    → store.schemas
    ├─ calculateNewCats(data,…) composables/nodes.js   → store.all_nodes (árboles D3)
    └─ calculate_status(…)      composables/filters.js → store.status
  store.current_collection_data = schemas.collections_dict[current_collection]
```

`store.schemas.collections_dict[snake_name]` es el objeto **`collection_data`** que baja como prop por casi todos los componentes del dashboard; es lo que dispara toda la resolución por convención. Las páginas son delgadas: `pages/dashboard/[group].vue` solo renderiza `<CollectionDisplay v-if="cats_ready" />`, y el middleware fija la colección activa desde el parámetro de ruta.

### Forma de `collection_data`

Del backend (`api/ps_schema/registry.py::_base_collection_dict`, líneas 176-195): `app_label`, `snake_name`, `model_name` (PascalCase, el `object_name` del modelo), `name`, `plural_name`, `level`, `cat_params`, `sort_fields`, `extra_massive_edit_fields`; más, por registry, `icon`, `color`, `open_insertion`, `available_actions` (`merge` / `massive_edit` / `massive_delete`), `xls_export`, `all_filters` y `fields[]`. Cada entrada de `fields[]` trae `name`, `real_name`, `primary_key`, `relation_type` (`simple|one_to_many|many_to_many|…`), `field_type`, `is_editable`, `null`, `width` y, si es relación, `related_snake_name` / `related_model` / `related_app_label`.

**En OCSA los metadatos derivados de los campos se calculan en el front**, en `composables/cats.js::calculateSchemas` (no en el backend):

| Propiedad | Cómo se calcula | Dónde |
|---|---|---|
| `pk` | campo con `primary_key`, si no `'id'` | `cats.js:26-27` |
| `name_field` | el primero de `name` / `title` que exista | `cats.js:28-33` |
| `has.{comments,description,help_text,order,color,icon}` | booleanos: ¿el modelo tiene ese campo? | `cats.js:17-18, 34-37` |
| `other_fields` | campos `simple` que no son pk, name_field ni de `has` | `cats.js:38-41` |
| `is_category` | `level.includes('category_')` → enruta a `/catalogs/` | `cats.js:73` |
| `child_relation_fields` | campos `one_to_many` / `many_to_many` → listas hijas | `cats.js:22-25` |
| `status_groups` | campos cuyo `related_model === 'StatusControl'`, con su `is_editable` | `cats.js:87-94` |
| `collection_filters` | la lista de filtros ensamblada y ordenada (§4) | `cats.js:53-108` |
| `available_sorts` | opciones del select «Ordenar por» | `cats.js:43-52, 95-113` |

`cat_params` se aplana al nivel superior, pero **las claves propias de la colección ganan**: `obj[coll.snake_name] = {...coll.cat_params || {}, ...coll}` (`cats.js:117`). Por eso `CollectionDisplay` lee `cat_params.init_display` por la ruta anidada (`CollectionDisplay.vue:181,185`), no por la aplanada.

## 2. La convención de autocarga (el núcleo)

Cada resolutor construye la ruta y hace `import()`; si el módulo no existe, el `.catch` importa un genérico. No hay registro, no hay glob, **no existe** un composable centralizado (`useDynamicComponent.js` no está en OCSA: la resolución está inline y duplicada en cuatro archivos).

```
~/components/dashboard/{app_label}/{snake_name}/{model_name}{Sufijo}.vue
```

Ejemplo real: `space_time` / `location` / `Location` → `~/components/dashboard/space_time/location/LocationHeader.vue`.

| Sufijo | Se resuelve en | Fallback | Rol |
|---|---|---|---|
| `Header` | `PanelList.vue:30,33-41` | `HeaderGeneric.vue` | fila colapsada del panel de expansión |
| `Sheet` | `PanelList.vue:31,43-52`; `DialogEdit.vue:32-33,53-64` (solo si `show_sheet`) | `SheetCommon.vue` | detalle expandido de solo lectura + colecciones hijas (§5) |
| `Edit` | `PanelCommon.vue:25-33`; `DialogEdit.vue:31,41-51` | `EditGeneric.vue` | campos del formulario, montados en el slot `#edit` de `EditCommon` |
| `EditSimple` | `PanelCommon.vue:36-44` | *(ninguno: queda vacío)* | editor inline completo que **reemplaza** a `EditCommon` |
| `Card` | `CardComponent.vue:20-30` | `CardGeneric.vue` | tarjeta compacta de un objeto |

`EditSimple` es el único sin fallback: su `.catch` asigna `''` (`PanelCommon.vue:44`), y el `v-if="edit_simple_component"` del template hace que el panel caiga al camino normal `EditCommon` + `{Model}Edit`.

**No hay aviso en consola** cuando falta un componente por modelo: un typo en el nombre cae silenciosamente al genérico. Es la forma más común de «no se ve mi componente».

### Edit vs EditSimple

En `PanelCommon.vue:176-200`:

- **Existe `{Model}EditSimple`** → se renderiza inline con `v-model="full_main"` y **nada más**: sin campos genéricos, sin botones Guardar/Eliminar de `EditCommon`. Es dueño de toda la UI de detalle y edición. En OCSA: `ParticipantEditSimple`, `EventEditSimple`, `ImpactEditSimple`, `DisplacementEditSimple`.
- **No existe** → `EditCommon` renderiza los campos genéricos (`EditCommonFields.vue`: nombre, orden, status, comentarios, ícono/color, descripción, help_text) y monta tu `{Model}Edit` en el slot `#edit`, con los botones Guardar/Eliminar.

> Aviso: `EditSimple` recibe **solo** `v-model` y **el padre no escucha ningún evento suyo**. `PanelCommon` no le pone `@item-saved`. Si un `EditSimple` cambia algo visible en la fila colapsada, la fila **no se entera**: la fila lee el objeto de la lista y el panel edita el objeto de detalle, y son objetos distintos. Sincronizarlos requiere cablear el emit primero (hoy no está).

### Props que recibe cada componente

| Componente | Props que entran | Eventos que el padre escucha |
|---|---|---|
| `Header` | `main` (la fila de la lista), `collection_data`, `show_details`, `parent`, `is_simple` | `@open-panel` → abre el panel (`PanelList.vue:111-119`) |
| `Sheet` | `full_main` (el detalle ya traído), `show_details`, `collection_data` | ninguno (`PanelList.vue:125-130`, `DialogEdit.vue:126-132`) |
| `Edit` | `v-model` (= `full_main`), `is_edit` | `@itemSaved` en `PanelCommon`; ninguno en `DialogEdit` |
| `EditSimple` | `v-model` únicamente | ninguno |
| `Card` | `full_main`, `title`, `note_id` | ninguno (`CardComponent.vue:34-41`) |

> `is_massive_edit` está declarado como prop en ~20 componentes `{Model}Edit.vue`, pero **ningún padre se lo pasa nunca**: siempre vale `false`. La edición masiva no reutiliza el `{Model}Edit`; `MassiveEdit.vue` arma su propio formulario a partir de `collection_data.fields` y de `extra_massive_edit_fields`, y `DialogEdit.vue:92-97` lo renderiza en lugar de `EditCommon` cuando `edit_type.key === 'massive_edit'`. La petición sale como `PATCH /{coll}/{primer_id}/massive_patch/`, decidido por `getLastId` en `store/index.js:17-19` a partir de la clave `elems_ids` del payload.

## 3. Árbol de componentes de una vista de lista

```
CollectionDisplay.vue        filtros, búsqueda (debounce 800 ms), orden, paginación, fetch
  ├─ chips de filtros + FiltersList.vue          (§4)
  └─ PanelsResult.vue        barra de acciones (crear/masivas), diálogo de alta y edición, paginación
       └─ PanelList.vue      resuelve {Model}Header y {Model}Sheet; v-for de filas
            └─ PanelCommon.vue  un panel de expansión; al abrir trae el detalle completo;
                                resuelve {Model}Edit y {Model}EditSimple
```

- `CollectionDisplay.vue` es la puerta de entrada y quien llama a `fetchElements`. Sus refs de estado (`results`, `final_filters`, `loading_fetch`, `total_count`, `q_value`) son **locales** al componente, lo cual permite anidar varios `CollectionDisplay` (§5). `composables/fetch.js` exporta refs equivalentes a nivel de módulo, pero está prácticamente muerto: lo único que alguien le importa hoy es `show_details` (`ProjectSheet.vue:10`). No lo uses para estado nuevo.
- `PanelCommon.openMain()` trae el objeto completo con `getElement(collection_data, id)` solo cuando se abre la fila: el endpoint de lista devuelve filas ligeras y el de detalle el objeto completo. Excepción: en `level === 'category_group'` no hay fetch, se usa la fila tal cual (`PanelCommon.vue:53-59`).
- La búsqueda (`q_value`) va con debounce de 800 ms; los cambios de `final_filters` disparan el refetch de inmediato por watcher profundo (`CollectionDisplay.vue:92-112`).

## 4. Barra de filtros automática

Los filtros del tope de cada lista se ensamblan en `cats.js` dentro de `collection_data.collection_filters` (ordenados por `order`) y los renderiza `FiltersList.vue`. Fuentes, en orden de ensamblaje:

1. **`all_filters`** declarados en el `CollectionSchema` del backend. Un `FilterRef` se resuelve contra `filters_dict` (los `FilterGroupSchema` registrados); un filtro custom sin `filter_name` se conserva con `is_custom: true` y `order: 12` (`cats.js:53-67`).
2. **Grupo de categoría** — si `is_category`, se agrega el `FilterGroupSchema` que corresponde al nivel, con `forced_level` y `order: 1` (`cats.js:73-86`).
3. **Status groups** — por cada campo relacionado con `StatusControl` se agrega su filtro de status y una opción de ordenamiento; si el schema marca el campo como no editable, el filtro viaja con `can_massive_edit: false` (`cats.js:87-101`).

`FiltersList.vue` despacha cada filtro a un widget según su forma:

| Forma del filtro | Widget |
|---|---|
| tiene `collection` | `StatusDetail` (select de status) |
| tiene `key_name` | `SelectGroup` (select jerárquico sobre los árboles D3 de `all_nodes`) |
| tiene `component` | custom: `TripleBooleanFilter`, `RangeDates`, `UserSelect`, `OnlyByFilter`, `LocationType`, `ConflictFilter` |

Los chips de arriba controlan qué filtros están visibles (`visible_filters`); con 3 filtros o menos, `simplified_filters` colapsa la fila de chips y pone los widgets junto al buscador (`CollectionDisplay.vue:76, 221-224`). Todos los widgets escriben en el mismo ref `final_filters`.

## 5. Colecciones hijas (objetos relacionados)

`SheetCommon.vue` es el detalle expandido genérico. Recorre `collection_data.child_relation_fields` y, por cada colección relacionada que exista en `schemas.collections_dict`, renderiza de una de dos formas:

- **Vienen los datos anidados** (`full_main['{snake}s']` es un array) → renderiza `PanelsResult` inline con `in_sheet`, sin fetch adicional.
- **Solo viene el conteo** (`full_main['{snake}s_count']`) → renderiza un `CollectionDisplay` anidado con `direct_sheet` y `init_filters={ [snake_del_padre]: id_del_padre }`: una sublista filtrada, con sus propios filtros y paginación, que se trae a demanda.

Un caso especial: en una colección `category_subtype`, las relaciones m2m hacia un `category_type` se omiten (`SheetCommon.vue:36-39`).

Así el detalle de un padre muestra a sus hijos sin una línea de código por modelo. Para personalizarlo, escribe un `{Model}Sheet.vue` que haga otra cosa —`ProjectSheet`, `ActorSheet`, `ParticipantTypeSheet` y `StatusProjectSheet` montan sus propios `CollectionDisplay`.

## 6. CRUD: colección vs categoría

`composables/save_elements.js` enruta toda escritura según `is_category`:

| | Normal (`is_category:false`) | Categoría (`is_category:true`) |
|---|---|---|
| Base de la API | `/{snake_name}/` | `/catalogs/{snake_name}/` |
| save / patch / delete | `saveSimple` / `patchSimple` / `deleteSimple` | `saveCatalog` / `patchCatalog` / `deleteCatalog` |
| efecto colateral | ninguno (el servidor es la fuente de verdad) | además muta `store.cats` en sitio y reconstruye `all_nodes` (o solo el filter group, en `patchCatalog`) |

`getLastId()` (`store/index.js:17-28`) decide POST vs PUT a partir del pk y de `is_new`, y desvía a `massive_patch/` cuando el payload trae `elems_ids`. `EditCommon` llama a `saveElement` / `deleteElement`; nunca habla con la API directamente.

### Contrato de retorno

Las acciones del store **devuelven `response.data` tal cual en el éxito** (no un envoltorio `{data}`) y `{errors: <cuerpo del error>}` en el fallo; los deletes devuelven `{success: true}`. `deleteSimple` tiene además un tercer caso: ante un 400 con `report_data` devuelve `{report_data}`, que alimenta el diálogo de borrado con reporte de dependencias (`store/index.js:185-197`). Quien llama distingue por la presencia de `res.errors`:

```js
const res = await saveElement(coll, obj)
if (res.errors) { /* manejarlo */ return }
useit(res)   // res ES el objeto guardado
```

No existe en OCSA un helper `ok`/`fail` ni `utils/api.js`: cada acción del store arma su propio `try/catch` y hace `console.error`. Los errores se muestran o inline (`EditCommon`) o con `showSnackbar` de `store/dash.js`.

### Nombres de eventos

Las plantillas usan listeners en kebab-case. Los canónicos: `item-saved` (`{res, is_new}`), `item-deleted` (id), `select-item`, `open-panel`, `finish-open`, `update-page-number`, `merge-items`, `massive-finish`, `change-status`, `apply-filters`. Ojo con la inconsistencia real: `PanelCommon` y `DialogEdit` escuchan `@itemSaved` en camelCase sobre el `{Model}Edit` dinámico, mientras que hacia arriba reemiten `item-saved`.

### Canarios intencionales en las plantillas

Algunos textos visibles son deliberados y no deberían aparecer nunca en el flujo normal; si aparecen, algo está mal cableado: `Sheet genérico 3` en `PanelCommon.vue`, `Acá estarán los campos de edición` en `EditGeneric.vue`, `HOLA TARJETA GENÉRICA` en `CardGeneric.vue`, `Sin data heredada!!` en `SheetCommon.vue`. No los borres.

## 7. Agregar una vista personalizada — checklist

1. Confirma que la colección existe en el registry del backend (skill `manage-collections`).
2. Decide el nivel de personalización:
   - **Solo una fila más rica** → `{Model}Header.vue`.
   - **Detalle de solo lectura o layout de hijos propio** → `{Model}Sheet.vue`.
   - **Campos de formulario dentro del marco genérico** → `{Model}Edit.vue`.
   - **Detalle + edición completamente a medida** → `{Model}EditSimple.vue` (reemplaza el marco genérico; recuerda que solo recibe `v-model` y que hoy nadie escucha sus eventos).
   - **Tarjeta compacta** → `{Model}Card.vue`.
3. Colócalo en `components/dashboard/{app_label}/{snake_name}/` con el nombre exacto `{model_name}{Sufijo}.vue` (modelo en PascalCase, carpeta en snake_case). El `app_label` y el `snake_name` son los del payload, no los que te parezcan.
4. No lo importes ni lo registres en ninguna parte. Y déjalo anotado mentalmente: a partir de ese momento, un grep de importadores dará cero.

## Archivos clave

| Tema | Archivo |
|---|---|
| Resolución Header + Sheet | `nuxt/components/dashboard/common/main/PanelList.vue` |
| Resolución Edit + EditSimple | `nuxt/components/dashboard/common/main/PanelCommon.vue` |
| Resolución Edit + Sheet (diálogo) | `nuxt/components/dashboard/common/dialog/DialogEdit.vue` |
| Resolución Card | `nuxt/components/dashboard/common/CardComponent.vue` |
| Payload → enriquecimiento del schema | `nuxt/composables/cats.js` |
| Árboles D3 de filtros | `nuxt/composables/nodes.js` |
| Enrutamiento del CRUD | `nuxt/composables/save_elements.js` |
| Store y acciones de API | `nuxt/store/index.js` |
| Entrada de la lista y filtros | `nuxt/components/dashboard/CollectionDisplay.vue` |
| Barra de acciones y diálogo de edición | `nuxt/components/dashboard/common/main/PanelsResult.vue` |
| Edición masiva | `nuxt/components/dashboard/common/MassiveEdit.vue` |
| Fallbacks genéricos | `nuxt/components/dashboard/common/generic/{HeaderGeneric,HeaderCommon,SheetCommon,EditGeneric,EditCommon,EditCommonFields,CardGeneric,CardCommon}.vue` |
| Widgets de filtros | `nuxt/components/dashboard/common/select/FiltersList.vue` |
| Contrato del backend | skill `manage-collections`, `api/ps_schema/registry.py`, `api/ps_schema/schemas.py` |
