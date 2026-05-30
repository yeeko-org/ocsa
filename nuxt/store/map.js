import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMainStore } from '~/store/index.js'

export const useMapStore = defineStore('map', () => {
  const mainStore = useMainStore()

  // --- Estado crudo ---
  // Fuente de verdad: las ubicaciones (features). Varias pueden
  // pertenecer al mismo proyecto.
  const projectLocations = ref({ type: 'FeatureCollection', features: [] })
  // Filtro de tipos de extractivismo seleccionados (ids).
  const selectedExtractivismTypes = ref([])
  // Contador de cargas listas (locations + catálogos = 2).
  const readyGets = ref(0)

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
    selectedExtractivismTypes,
    readyGets,
    uniqueProjects,
    searchableProjects,
    extractivismTypeProps,
    loadData,
    hydrateProjectLocations,
  }
})