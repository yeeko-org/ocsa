// Geometría compartida entre el rail (Capa A) y las filas de chips (Capa B)
// para que cada fila de chips quede alineada a su ícono.
//   rowH: alto de cada fila (≈ v-btn size large). chipsTop salta el botón
//   menu (primera fila del rail). chipsLeft libra el ancho del rail.
export const RAIL_GEOMETRY = {
  top: 76,
  left: 8,
  rowH: 56,  // rowH = pitch real del v-btn large
  chipsLeft: 76,    // left + ancho del rail + gap
  chipsTop: 144,    // centra el primer bloque con su ícono (bajo el botón menu)
  expandedExtra: 196,  // px que se desplazan los chips con el rail expandido
}

// Registro declarativo de los filtros del mapa (decisions §4). Config
// ESTÁTICA: declara solo lo que NO se puede derivar del backend. El resto
// (name/plural/description, opciones y —para eventos/afectaciones— también
// icon/color/label) lo resuelve `store/map.js` desde `schemas`/`all_nodes`.
//
//  - `filterGroup`: key_name del FilterGroupSchema del que cuelga.
//  - `groupId`: id fijo del CatalogGroup (event_group/impact_group) cuando un
//    mismo filter_group alimenta varias filas (ocs-entities): violencia=1,
//    acciones=2, legal=3; afectación social=1, ecológica=2.
//  - `selects[].level`: 'type' = hijos del nodo base; 'subtype' = hojas.
//  - `selects[].conditional`: el select solo se puebla con los hijos de los
//    tipos ya seleccionados (subtipos de afectación).
//  - `selects[].facet`: letra de la dimensión en el payload de facetas contra
//    la que se filtra en cliente (e=evento, i=afectación, s=subtipo,
//    p=participación; 'p' ya no la consume nadie: las posiciones pasaron a
//    `actor_projects`). `selects[].geoIndex` ('megaproject' | 'state') es la
//    alternativa para dimensiones derivadas del geojson; excluyente con facet.
//    De aquí se genera el filtrado (store/map.js): añadir un filtro no obliga
//    a tocar la lógica de intersección.
//  - `purposeFacet`: letra de faceta del toggle `purposeKey` (legal → 'u').
//    Pendiente en el backend; mientras no exista en el payload, no recorta.
//  - `label`/`icon`/`color`: overrides; se omiten cuando el nodo de grupo ya
//    los trae (eventos/afectaciones heredan del event_group/impact_group).

export const FILTER_REGISTRY = [
  {
    id: 'megaproject', filterGroup: 'project_types',
    label: 'Tipos de proyecto', icon: 'factory', color: 'deep-purple',
    // El extractivismo se elige en la leyenda (v-chip-group), no aquí; el
    // drill-down del autocomplete sigue leyendo filters.extractivism.
    selects: [
      { stateKey: 'megaproject', level: 'subtype', picker: 'autocomplete',
        geoIndex: 'megaproject' },
    ],
  },
  {
    id: 'violence', filterGroup: 'event_types', groupId: 1,
    label: 'Eventos de violencia',
    selects: [
      { stateKey: 'violence', level: 'subtype', picker: 'checkbox',
        facet: 'e' },
    ],
  },
  {
    id: 'collectiveActions', filterGroup: 'event_types', groupId: 2,
    selects: [
      { stateKey: 'collectiveActions', level: 'subtype', picker: 'checkbox',
        facet: 'e' },
    ],
  },
  {
    id: 'legal', filterGroup: 'event_types', groupId: 3,
    purposeKey: 'legalPurpose', purposeFacet: 'u',
    selects: [
      { stateKey: 'legal', level: 'subtype', picker: 'checkbox', facet: 'e' },
    ],
  },
  {
    id: 'socialImpacts', filterGroup: 'impact_types', groupId: 1,
    label: 'Afectaciones sociales',
    selects: [
      { stateKey: 'socialImpacts', level: 'type', picker: 'checkbox',
        facet: 'i' },
      { stateKey: 'socialImpactSubtypes', level: 'subtype',
        picker: 'select', conditional: true, facet: 's' },
    ],
  },
  {
    id: 'environmentalImpacts', filterGroup: 'impact_types', groupId: 2,
    label: 'Afectaciones ambientales',
    selects: [
      { stateKey: 'environmentalImpacts', level: 'type', picker: 'checkbox',
        facet: 'i' },
      { stateKey: 'environmentalImpactSubtypes', level: 'subtype',
        picker: 'select', conditional: true, facet: 's' },
    ],
  },
  {
    id: 'states', filterGroup: 'states', label: 'Entidad federativa',
    icon: 'map', color: 'brown', chipField: 'code_name', maxCells: 8,
    selects: [
      { stateKey: 'states', level: 'subtype', picker: 'autocomplete',
        geoIndex: 'state' },
    ],
  },
  {
    // Grupo a medida (sin `selects`): actor y posición se resuelven juntos en
    // store/map.js contra `actor_projects` (/map/actors/), no por el loop
    // genérico. Van juntos porque la unidad del dato es el par
    // (actor, proyecto): la posición se sostiene en un proyecto concreto.
    id: 'actors', filterGroup: 'participant_types',
    label: 'Actores y sus posiciones', icon: 'groups', color: 'blue',
    custom: true,
  },
]