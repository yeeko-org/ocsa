import { defineStore } from 'pinia'
import { ref, reactive, shallowRef, computed } from 'vue'
import { useMainStore } from '~/store/index.js'

export const useMapStore = defineStore('map', () => {
  const mainStore = useMainStore()

  // --- Estado crudo ---
  // Fuente de verdad: las ubicaciones (features). Varias pueden
  // pertenecer al mismo proyecto.
  // shallowRef (no ref): el GeoJSON se asigna una sola vez y se entrega a
  // Mapbox de forma imperativa; hacerlo profundamente reactivo convertía
  // cada feature en un proxy y disparaba un O(n^2) en hydrateProjectLocations
  // (~121 s con 950 features). Con shallowRef solo la reasignación de .value
  // es reactiva; los features quedan como objetos planos.
  const projectLocations = shallowRef({ type: 'FeatureCollection', features: [] })
  // Estado de filtros unificado y URL-serializable (decisions §4, §15).
  // Cada clave es un filtro; los arrays guardan ids. `extractivism` vacío
  // = "todos" (sin filtrar), igual que el ref aislado que reemplaza.
  const filters = reactive({
    extractivism: [],          // ids extractivism_type (vacío = todos)
    megaproject: [],           // ids megaproject_type
    violence: [],              // ids event_type (grupo violencia)
    collectiveActions: [],     // ids event_type (grupo acciones colectivas)
    legal: [],                 // ids event_type (grupo mecanismos legales)
    legalPurpose: [],          // ids purpose (toggle despojo/defensa)
    socialImpacts: [],         // ids impact_type (grupo social)
    environmentalImpacts: [],  // ids impact_type (grupo ambiental)
    states: [],                // ids state (múltiple)
    actors: [],                // [{ id, name }] aplicados (stub hasta sesión 4)
    positions: [],             // ids participant_group activos
    positionTypes: {},         // { [groupId]: [participant_type ids] }
  })

  // Estado de UI compartido entre el rail y las cápsulas (no es estado de
  // datos, pero lo coordinan dos componentes hermanos → vive en el store).
  // Un solo picker abierto a la vez (decisions §4.2); null = ninguno.
  const activePickerKey = ref(null)
  // Extractivismo pre-activado/expandido por defecto (decisions §5): su
  // tira de chips de color (la leyenda) se ve al cargar.
  const showExtractivismLegend = ref(true)
  // Contador de cargas listas (locations + catálogos = 2).
  const readyGets = ref(0)
  // Id del proyecto cuyo detalle está abierto. Fuente de verdad única
  const targetProjectId = ref(null)

  // Resuelve color/ícono/extractivismo a partir del megaproject_type.
  // Espejo exacto de la lógica original de hidratación: si no hay
  // megaproject_type solo devuelve color base y extractivismo vacío.
  function resolveExtractivism(mp_type_id) {
    if (!mp_type_id) {
      return { color: '#03fcd7', extractivism_type: null, extractivism_types: [] }
    }
    const mp_obj = mainStore.megaproject_types_dict[mp_type_id] || {}
    const first = mp_obj.first_extractivism_type
    const icon = first?.icon || 'harbor'
    const extr_types = mp_obj.extractivism_types || []
    return {
      color: first?.color || '#808080',
      icon,
      icon_pin: `${icon}-pin`,
      extractivism_type: first?.id || null,
      extractivism_types: extr_types,
      power: extr_types.length === 1 ? 2 : 1,
    }
  }

  // --- Getters derivados ---
  // Lista única de proyectos (deduplicada por id), autosuficiente:
  // calcula su extractivismo sin depender de hydrateProjectLocations.
  const uniqueProjects = computed(() => {
    const seen = new Map()
    for (const feature of projectLocations.value.features) {
      const project = feature.properties?.project
      if (!project || seen.has(project.id)) continue
      const extr = resolveExtractivism(project.megaproject_type)
      seen.set(project.id, {
        ...project,
        // Solo para filtrar; NO usar 'extractivism_types' porque ese nombre
        // cortocircuita el lookup de íconos de ExtractivismIcons.
        extractivism_type_ids: extr.extractivism_types,
        color: extr.color,
      })
    }
    return [...seen.values()]
  })

  // Proyección ligera para el buscador: { id, name, label } ordenada.
  const searchableProjects = computed(() =>
    uniqueProjects.value
      .map(p => {
        const label = p.alternative_name
          ? `${p.name} (${p.alternative_name})`
          : p.name
        return { id: p.id, name: p.name, label }
      })
      .sort((a, b) => a.name.localeCompare(b.name))
  )

  // Props de extractivismo para los clusters del mapa (colores/íconos/ids).
  const extractivismTypeProps = computed(() => {
    const et_props = { colors: [], icons: [], ids: [] }
    const cats = mainStore.cats
    if (!cats) return et_props
    cats.extractivism_type.forEach(et => {
      et_props.colors.push(et.color)
      et_props.icons.push(et.icon)
      et_props.ids.push(et.id)
    })
    return et_props
  })

  // --- Opciones de filtros (derivadas de cats/geo) ---
  const extractivismOptions = computed(
    () => mainStore.cats?.extractivism_type || [])
  const purposeOptions = computed(() => mainStore.cats?.purpose || [])
  const stateOptions = computed(() => mainStore.cats?.state || [])

  // Megaproyecto: drill-down. Solo los MegaprojectType cuyos
  // extractivism_types (M2M) intersecten con el extractivismo activo. Sin
  // extractivismo activo → sin opciones (el ícono queda deshabilitado, §6).
  const megaprojectOptions = computed(() => {
    const active = filters.extractivism
    if (!active.length) return []
    return (mainStore.cats?.megaproject_type || []).filter(mp =>
      (mp.extractivism_types || []).some(id => active.includes(id)))
  })

  // Eventos: cada grupo se resuelve por su bandera de catálogo y se listan
  // sus EventType (FK event_type.event_group → event_group.id).
  const eventGroups = computed(() => mainStore.cats?.event_group || [])
  const violenceGroup = computed(() =>
    eventGroups.value.find(g => g.model_origin === 'HechosViolencia'))
  const collectiveActionsGroup = computed(() =>
    eventGroups.value.find(g => g.model_origin === 'FormaAC'))
  const legalGroup = computed(() =>
    eventGroups.value.find(g => g.show_position))
  const eventTypesByGroup = groupId =>
    (mainStore.cats?.event_type || []).filter(et => et.event_group === groupId)
  const violenceOptions = computed(() =>
    violenceGroup.value ? eventTypesByGroup(violenceGroup.value.id) : [])
  const collectiveActionOptions = computed(() =>
    collectiveActionsGroup.value
      ? eventTypesByGroup(collectiveActionsGroup.value.id) : [])
  const legalOptions = computed(() =>
    legalGroup.value ? eventTypesByGroup(legalGroup.value.id) : [])

  // Impactos: grupo social (is_social) vs ambiental (el resto).
  const impactGroups = computed(() => mainStore.cats?.impact_group || [])
  const impactTypesByGroup = groupId =>
    (mainStore.cats?.impact_type || []).filter(it => it.impact_group === groupId)
  const socialImpactGroup = computed(() =>
    impactGroups.value.find(g => g.is_social))
  const environmentalImpactGroup = computed(() =>
    impactGroups.value.find(g => !g.is_social))
  const socialImpactOptions = computed(() =>
    socialImpactGroup.value
      ? impactTypesByGroup(socialImpactGroup.value.id) : [])
  const environmentalImpactOptions = computed(() =>
    environmentalImpactGroup.value
      ? impactTypesByGroup(environmentalImpactGroup.value.id) : [])

  // Actores/posiciones: ParticipantGroup y sus ParticipantType.
  const positionGroups = computed(() => mainStore.cats?.participant_group || [])
  const positionTypeOptions = groupId =>
    (mainStore.cats?.participant_type || [])
      .filter(pt => pt.participant_group === groupId)

  // --- Helpers de filtros (cápsulas, limpiar, payload) ---
  // Resuelve un id a su etiqueta legible dentro de un catálogo.
  function labelFrom(list, id) {
    const item = list.find(x => x.id === id)
    return item ? (item.short_name || item.name) : `#${id}`
  }

  // Cápsulas activas (decisions §4.3). Excluye extractivismo: ese tiene su
  // propia tira de chips de color (la leyenda, §5). Cada cápsula lleva su
  // filterKey para poder cerrarla o reabrir su picker.
  const activeCapsules = computed(() => {
    const caps = []
    const add = (filterKey, ids, list) => ids.forEach(id =>
      caps.push({ filterKey, value: id, label: labelFrom(list, id) }))
    add('megaproject', filters.megaproject, mainStore.cats?.megaproject_type || [])
    add('violence', filters.violence, violenceOptions.value)
    add('collectiveActions', filters.collectiveActions, collectiveActionOptions.value)
    add('legal', filters.legal, legalOptions.value)
    add('legalPurpose', filters.legalPurpose, purposeOptions.value)
    add('socialImpacts', filters.socialImpacts, socialImpactOptions.value)
    add('environmentalImpacts', filters.environmentalImpacts, environmentalImpactOptions.value)
    add('states', filters.states, stateOptions.value)
    add('positions', filters.positions, positionGroups.value)
    // Sub-posiciones: la cápsula recuerda su grupo para poder cerrarla.
    Object.entries(filters.positionTypes).forEach(([groupId, ids]) =>
      (ids || []).forEach(id => caps.push({
        filterKey: 'positionTypes', groupId: Number(groupId), value: id,
        label: labelFrom(positionTypeOptions(Number(groupId)), id),
      })))
    // Actores: ya traen su nombre (no están en cats).
    filters.actors.forEach(a =>
      caps.push({ filterKey: 'actors', value: a.id, label: a.name }))
    return caps
  })

  // ¿Hay algún filtro activo? Controla la franja y "limpiar todo".
  const hasActiveFilters = computed(() =>
    activeCapsules.value.length > 0 || filters.extractivism.length > 0)

  // Quita un valor concreto de un filtro (cerrar una cápsula).
  function removeCapsule(cap) {
    const { filterKey, value, groupId } = cap
    if (filterKey === 'actors')
      filters.actors = filters.actors.filter(a => a.id !== value)
    else if (filterKey === 'positionTypes')
      filters.positionTypes[groupId] =
        (filters.positionTypes[groupId] || []).filter(v => v !== value)
    else if (Array.isArray(filters[filterKey]))
      filters[filterKey] = filters[filterKey].filter(v => v !== value)
  }

  // Vacía todos los filtros de golpe (decisions §4 "limpiar todo").
  function clearAllFilters() {
    filters.extractivism = []
    filters.megaproject = []
    filters.violence = []
    filters.collectiveActions = []
    filters.legal = []
    filters.legalPurpose = []
    filters.socialImpacts = []
    filters.environmentalImpacts = []
    filters.states = []
    filters.actors = []
    filters.positions = []
    filters.positionTypes = {}
  }

  // Payload listo para el backend (punto de integración de la Sesión 4).
  // Hoy solo `extractivism` se aplica de verdad (useMapLayers); el resto se
  // acumula aquí a la espera del contrato de la API de filtros.
  const filterPayload = computed(() => {
    const payload = {}
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        if (value.length) payload[key] = value
      } else if (value && Object.keys(value).length) {
        payload[key] = value
      }
    })
    return payload
  })

  // --- Acciones ---
  function loadData() {
    mainStore.getProjectLocations().then(locations => {
      projectLocations.value = locations
      readyGets.value += 1
    })
    mainStore.fetchCatalogs().then(() => {
      readyGets.value += 1
    })
  }

  // Decora cada feature con color/ícono/power para las capas del mapa.
  function hydrateProjectLocations() {
    projectLocations.value.features.forEach(feature => {
      const props = feature.properties
      Object.assign(props, resolveExtractivism(props.project?.megaproject_type))
    })
  }

  return {
    projectLocations,
    readyGets,
    targetProjectId,
    uniqueProjects,
    searchableProjects,
    extractivismTypeProps,
    loadData,
    hydrateProjectLocations,
    // --- Filtros ---
    filters,
    activePickerKey,
    showExtractivismLegend,
    // Opciones derivadas
    extractivismOptions,
    megaprojectOptions,
    violenceOptions,
    collectiveActionOptions,
    legalOptions,
    socialImpactOptions,
    environmentalImpactOptions,
    stateOptions,
    purposeOptions,
    positionGroups,
    positionTypeOptions,
    // Helpers
    activeCapsules,
    hasActiveFilters,
    removeCapsule,
    clearAllFilters,
    filterPayload,
  }
})