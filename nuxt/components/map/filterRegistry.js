// Geometría compartida entre el rail (Capa A) y las filas de chips (Capa B)
// para que cada fila de chips quede alineada a su ícono. Valores tentativos;
// el encaje fino responsive es de la Sesión 5.
//   rowH: alto de cada fila (≈ v-btn size large). chipsTop salta el botón
//   menu (primera fila del rail). chipsLeft libra el ancho del rail.
export const RAIL_GEOMETRY = {
  top: 76, left: 8, rowH: 48,  // rowH = pitch real del v-btn large (44) + gap 4
  chipsLeft: 76,    // left + ancho del rail + gap
  chipsTop: 126,    // centra el primer bloque con su ícono (bajo el botón menu)
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
//  - `label`/`icon`/`color`: overrides; se omiten cuando el nodo de grupo ya
//    los trae (eventos/afectaciones heredan del event_group/impact_group).

export const FILTER_REGISTRY = [
  {
    id: 'megaproject', filterGroup: 'project_types',
    label: 'Tipos de Megaproyectos', icon: 'factory', color: 'deep-purple',
    // El extractivismo se elige en la leyenda (v-chip-group), no aquí; el
    // drill-down del autocomplete sigue leyendo filters.extractivism.
    selects: [
      { stateKey: 'megaproject', level: 'subtype', picker: 'autocomplete' },
    ],
  },
  {
    id: 'violence', filterGroup: 'event_types', groupId: 1,
    label: 'Eventos de violencia',
    selects: [{ stateKey: 'violence', level: 'subtype', picker: 'checkbox' }],
  },
  {
    id: 'collectiveActions', filterGroup: 'event_types', groupId: 2,
    selects: [
      { stateKey: 'collectiveActions', level: 'subtype', picker: 'checkbox' },
    ],
  },
  {
    id: 'legal', filterGroup: 'event_types', groupId: 3,
    purposeKey: 'legalPurpose',
    selects: [{ stateKey: 'legal', level: 'subtype', picker: 'checkbox' }],
  },
  {
    id: 'socialImpacts', filterGroup: 'impact_types', groupId: 1,
    label: 'Afectaciones sociales',
    selects: [
      { stateKey: 'socialImpacts', level: 'type', picker: 'checkbox' },
      { stateKey: 'socialImpactSubtypes', level: 'subtype',
        picker: 'select', conditional: true },
    ],
  },
  {
    id: 'environmentalImpacts', filterGroup: 'impact_types', groupId: 2,
    label: 'Afectaciones ambientales',
    selects: [
      { stateKey: 'environmentalImpacts', level: 'type', picker: 'checkbox' },
      { stateKey: 'environmentalImpactSubtypes', level: 'subtype',
        picker: 'select', conditional: true },
    ],
  },
  {
    id: 'states', filterGroup: 'states', label: 'Entidad federativa',
    icon: 'map', color: 'brown', chipField: 'code_name', maxCells: 8,
    selects: [
      { stateKey: 'states', level: 'subtype', picker: 'autocomplete' },
    ],
  },
  {
    id: 'actors', filterGroup: 'participant_types',
    label: 'Actores y sus posiciones', icon: 'groups', color: 'blue',
    custom: true,
  },
]