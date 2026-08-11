import { defineStore } from 'pinia'
import { ref, reactive, shallowRef, computed, watch } from 'vue'
import { useMainStore } from '~/store/index.js'
import { FILTER_REGISTRY } from '~/components/map/filters/filterRegistry.js'
import {
  buildProjectIndex, buildActorIndex, runSearch,
} from '~/components/map/common/searchIndex.js'

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
  // Índice invertido de facetas en memoria. Se construye una sola vez al cargar
  // el payload; shallowRef porque son Maps grandes que se asignan de golpe
  // (mismo criterio que projectLocations: evitar proxies por feature).
  const facetIndex = shallowRef(null)  // { e:Map, i:Map, s:Map, p:Map }
  const facetsReady = ref(false)
  // Actores (api-contract §2). shallowRef por el mismo motivo que facetIndex:
  // Maps grandes que se asignan de golpe.
  const actorProjects = shallowRef(null)  // Map<actorId, Set<projId>> (invertido)
  const actorsById = shallowRef(null)     // Map<id, actor>
  const actorsReady = ref(false)
  // Instancias MiniSearch compartidas (buscador global ↔ actores). shallowRef:
  // el índice es un objeto pesado que se reemplaza entero al construirse.
  const projectSearchIndex = shallowRef(null)
  const actorSearchIndex = shallowRef(null)
  // Guard de build concurrente: dos ensureActors() simultáneos (focus del
  // buscador + apertura del picker) comparten esta promesa y no reconstruyen
  // los índices dos veces. Variable de instancia del store (no reactiva).
  let actorsPromise = null
  // Estado de filtros unificado y URL-serializable (decisions §4, §15).
  // Cada clave es un filtro; los arrays guardan ids. `extractivism` vacío
  // = "todos" (sin filtrar), igual que el ref aislado que reemplaza.
  const filters = reactive({
    extractivism: [],                 // ids extractivism_type
    megaproject: [],                  // ids megaproject_type
    violence: [],                     // ids event_type (grupo violencia)
    collectiveActions: [],            // ids event_type (acciones colectivas)
    legal: [],                        // ids event_type (mecanismos legales)
    legalPurpose: [],                 // ids purpose (toggle despojo/defensa)
    socialImpacts: [],                // ids impact_type (grupo social)
    socialImpactSubtypes: [],         // ids impact_subtype (social, condic.)
    environmentalImpacts: [],         // ids impact_type (grupo ambiental)
    environmentalImpactSubtypes: [],  // ids impact_subtype (ambiental, cond.)
    states: [],                       // ids state
    actors: [],                       // [{ id, name }]
    positions: [],                    // ids participant_group activos
    positionTypes: {},                // { [groupId]: [participant_type ids] }
  })

  // Estado de UI compartido por componentes hermanos (rail + filas de
  // chips), no es estado de datos → vive en el store. Un solo picker
  // abierto a la vez (decisions §4.2); null = ninguno.
  const activePickerKey = ref(null)
  // Rail expandido (muestra nombres) y modo "etiquetas comprimidas" (un solo
  // chip "{n} filtros" por grupo). Estado de UI compartido rail ↔ chips.
  const railExpanded = ref(false)
  const chipsCompact = ref(false)
  const toggleRailExpanded = () => { railExpanded.value = !railExpanded.value }
  const toggleChipsCompact = () => { chipsCompact.value = !chipsCompact.value }
  // Abrir un picker colapsa el rail expandido.
  watch(activePickerKey, key => { if (key) railExpanded.value = false })
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

  // --- Índices y filtrado en cliente (api-contract) ---
  // Construye Map<catId, Set<projectId>> desde un accessor que da el/los id(s)
  // de la dimensión para cada proyecto. Normaliza escalar|array.
  function buildIndexFromProjects(projects, accessor) {
    const index = new Map()
    for (const p of projects) {
      const raw = accessor(p)
      if (raw == null) continue
      const ids = Array.isArray(raw) ? raw : [raw]
      for (const id of ids) {
        if (id == null) continue
        let set = index.get(id)
        if (!set) index.set(id, set = new Set())
        set.add(p.id)
      }
    }
    return index
  }

  // Dimensiones derivadas del geojson (siempre disponibles, sin backend nuevo).
  const extractivismIndex = computed(() =>
    buildIndexFromProjects(uniqueProjects.value, p => p.extractivism_type_ids))
  const megaprojectIndex = computed(() =>
    buildIndexFromProjects(uniqueProjects.value, p => p.megaproject_type))
  // El estado NO es campo del proyecto: viaja como hermano de `project` dentro
  // de properties (una feature por ubicación). Por eso este índice recorre las
  // features y no los proyectos deduplicados. Un proyecto con ubicaciones en
  // varios estados se indexa por unión: aparece al filtrar por cualquiera de
  // ellos. La clave es el id numérico tal cual llega del backend, que es el
  // mismo que guardan filters.states (ids de State).
  const stateIndex = computed(() => {
    const index = new Map()
    for (const feature of projectLocations.value.features) {
      const { state, project } = feature.properties || {}
      if (state == null || !project) continue
      let set = index.get(state)
      if (!set) index.set(state, set = new Set())
      set.add(project.id)
    }
    return index
  })

  // Universo: todos los ids de proyecto (base de la intersección sin filtros).
  const allProjectIds = computed(() =>
    new Set(uniqueProjects.value.map(p => p.id)))

  // participant_group → [participant_type ids]: resuelve el filtro de
  // "posiciones" (guardado por grupo) contra las facetas `p` (por tipo).
  const participantTypesByGroup = computed(() => {
    const map = new Map()
    ;(mainStore.cats?.participant_type || []).forEach(pt => {
      let arr = map.get(pt.participant_group)
      if (!arr) map.set(pt.participant_group, arr = [])
      arr.push(pt.id)
    })
    return map
  })

  // Una pasada sobre el payload directo → un índice invertido por cada
  // dimensión (letra) presente. NO hardcodea las letras: construye las que
  // existan (e/i/s/p hoy; p.ej. 'u' de purpose cuando el backend la agregue,
  // sin tocar este código). Clave ausente = el proyecto no contribuye a ella.
  function buildFacetIndex(facets) {
    const dims = {}
    for (const [projId, dimObj] of Object.entries(facets)) {
      const pid = Number(projId)
      for (const [letter, ids] of Object.entries(dimObj)) {
        if (!ids) continue
        let target = dims[letter]
        if (!target) dims[letter] = target = new Map()
        for (const id of ids) {
          let set = target.get(id)
          if (!set) target.set(id, set = new Set())
          set.add(pid)
        }
      }
    }
    return dims
  }

  // OR dentro de un grupo: unión de los Sets de los ids seleccionados. null si
  // no hay ids (dimensión inactiva → no recorta). Un Set vacío sí recorta (ids
  // que no matchean nada vacían la intersección).
  function unionFromIndex(index, ids) {
    if (!ids || !ids.length) return null
    const out = new Set()
    for (const id of ids) {
      const set = index.get(id)
      if (set) for (const v of set) out.add(v)
    }
    return out
  }

  // Intersección AND iterando el Set menor.
  function intersect(a, b) {
    const [small, big] = a.size <= b.size ? [a, b] : [b, a]
    const out = new Set()
    for (const v of small) if (big.has(v)) out.add(v)
    return out
  }

  // Índice (Map<catId, Set<projId>>) de una faceta del payload; null si esa
  // letra aún no existe (p.ej. 'u' antes de que el backend la emita) → ese
  // filtro simplemente no recorta.
  const indexForFacet = letter => facetIndex.value?.[letter] || null

  // Proyectos visibles: AND entre grupos de las uniones OR de cada dimensión
  // activa ("OR intra, AND inter", decisions §7). Sin filtros → todos. El Set
  // es de project.id únicos, así que sirve también de contador.
  //
  // El mapeo dimensión→índice se DERIVA del registro (filterRegistry.js): cada
  // select trae `facet` (payload) o `geoIndex` (geojson). Añadir un filtro no
  // obliga a tocar esta lógica.
  const visibleProjectIds = computed(() => {
    const groups = []
    const push = set => { if (set) groups.push(set) }
    const geo = {
      extractivism: extractivismIndex.value,
      megaproject: megaprojectIndex.value,
      state: stateIndex.value,
    }
    const indexFor = sel =>
      sel.facet ? indexForFacet(sel.facet) : geo[sel.geoIndex]

    // Extractivismo no vive en el registro (se elige en la leyenda, §5).
    push(unionFromIndex(geo.extractivism, filters.extractivism))

    for (const reg of FILTER_REGISTRY) {
      for (const sel of reg.selects || []) {
        const idx = indexFor(sel)
        if (idx) push(unionFromIndex(idx, filters[sel.stateKey]))
      }
      // Toggle de propósito (legal): faceta aparte del select. Mientras el
      // backend no emita `purposeFacet`, indexForFacet devuelve null y no
      // recorta (el chip sigue visible).
      if (reg.purposeKey && reg.purposeFacet) {
        const idx = indexForFacet(reg.purposeFacet)
        if (idx) push(unionFromIndex(idx, filters[reg.purposeKey]))
      }
    }

    // Actores/posiciones (grupo custom, faceta de participación 'p').
    const fp = indexForFacet('p')
    if (fp) {
      // Sub-posiciones: ids de participant_type directos.
      push(unionFromIndex(fp, Object.values(filters.positionTypes).flat()))
      // Posiciones: cada grupo se expande a sus participant_type ids.
      const posIds = filters.positions.flatMap(
        g => participantTypesByGroup.value.get(g) || [])
      push(unionFromIndex(fp, posIds))
    }
    // Actores: OR entre los actores elegidos (unión de sus conjuntos de
    // proyectos). `actorProjects` ya viene invertido (actor→proyectos), así que
    // se reusa `unionFromIndex` igual que cualquier otra dimensión. Si el
    // payload aún no cargó (actorProjects null), no recorta; al poblarse el
    // shallowRef, este computed se reevalúa solo.
    if (actorProjects.value)
      push(unionFromIndex(actorProjects.value, filters.actors.map(a => a.id)))

    if (!groups.length) return allProjectIds.value
    return groups.reduce(intersect)
  })

  // --- Resolución del registro de filtros (decisions §4, "mixin") ---
  // El registro estático vive en `components/map/filterRegistry.js`; aquí
  // solo la parte reactiva: navegar `all_nodes` y heredar metadatos.
  const groupById = id => FILTER_REGISTRY.find(g => g.id === id)

  // Nodo d3 base (nivel 'type') de un grupo: la raíz del filter_group o, si
  // declara `groupId`, el CatalogGroup con ese id (event_group/impact_group).
  function baseNode(rg) {
    const root = mainStore.all_nodes?.[rg.filterGroup]
    if (!root) return null
    if (!rg.groupId) return root
    return (root.children || []).find(c => c.data.id === rg.groupId) || null
  }

  // Mixin: funde la entrada del registro con el filter_group de schemas
  // (name/plural/description) y, para eventos/afectaciones, deriva
  // label/icon/color del nodo de grupo cuando el registro no los declara.
  // Precedencia: override del registro → nodo de grupo → meta del filter_group.
  const resolveGroup = id => {
    const rg = groupById(id)
    if (!rg) return null
    const meta = mainStore.schemas?.filters_dict?.[rg.filterGroup] || {}
    const node = rg.groupId ? baseNode(rg)?.data : null
    return {
      ...meta, ...rg,
      label: rg.label || node?.name || meta.name,
      icon: rg.icon || node?.icon,
      color: rg.color || node?.color,
      description: node?.description || meta.description,
    }
  }

  // Opciones (.data de los nodos) de un `select` concreto del grupo.
  // Resuelve el nivel del árbol y los casos especiales: drill-down de
  // megaproyecto (hojas filtradas por el extractivismo activo) y subtipos
  // condicionales de afectación (hijos de los tipos seleccionados).
  function optionsFor(id, stateKey) {
    const rg = groupById(id)
    if (!rg || !rg.selects) return []
    const sel = rg.selects.find(s => s.stateKey === stateKey) || rg.selects[0]
    const root = mainStore.all_nodes?.[rg.filterGroup]
    const base = baseNode(rg)
    if (!base) return []
    if (sel.level === 'type')
      return (base.children || []).map(c => c.data)
    if (sel.conditional) {
      const typeKey = rg.selects.find(s => s.level === 'type')?.stateKey
      const selected = filters[typeKey] || []
      return (base.children || [])
        .filter(t => selected.includes(t.data.id))
        .flatMap(t => (t.children || []).map(c => c.data))
    }
    if (id === 'megaproject') {
      const ext = filters.extractivism
      const extNodes = ext.length
        ? (root.children || []).filter(e => ext.includes(e.data.id))
        : (root.children || [])
      return extNodes.flatMap(e => (e.children || []).map(c => c.data))
    }
    return (base.children || []).map(c => c.data)
  }

  const purposeOptions = computed(() => mainStore.cats?.purpose || [])
  // Actores/posiciones: ParticipantGroup y sus ParticipantType.
  const positionGroups = computed(() => mainStore.cats?.participant_group || [])
  const positionTypeOptions = groupId =>
    (mainStore.cats?.participant_type || [])
      .filter(pt => pt.participant_group === groupId)

  // --- Helpers de chips/cápsulas (decisions §4.3) ---
  // Acorta etiquetas largas para los chips de fila (corta en 32 + …).
  function truncate(text) {
    const t = String(text ?? '')
    return t.length > 36 ? `${t.slice(0, 32)}…` : t
  }

  const positionGroupById = id => positionGroups.value.find(g => g.id === id)
  const positionTypeById = (groupId, id) =>
    positionTypeOptions(groupId).find(pt => pt.id === id)

  // Construye un chip a partir de una categoría resuelta. `value` siempre
  // guarda el id (aunque la categoría no esté cargada) para poder cerrarlo.
  function makeChip(rg, stateKey, id, item, extra = {}) {
    const raw = item?.[rg.chipField] || item?.short_name || item?.name
    return {
      groupId: rg.id, stateKey, value: id,
      label: truncate(raw ?? `#${id}`),
      full: item?.name ?? `#${id}`, description: item?.description || '',
      color: item?.color || rg.color, icon: item?.icon || null, ...extra,
    }
  }

  // Cápsulas agrupadas por rail-group (Capa B). Cada grupo expone `blocks`:
  // un array de "bloques" de chips. Los grupos normales tienen un único
  // bloque; Actores tiene dos (actores | posiciones) cuando ambos están
  // activos, para poder pintar una banda por cada uno. Cada bloque se dibuja
  // como una cuadrícula adaptativa (ver FilterChips), limitada a `maxCells`.
  const capsulesByGroup = computed(() => FILTER_REGISTRY.map(reg => {
    const rg = resolveGroup(reg.id)   // con label/icon/color derivados
    const maxCells = reg.maxCells || 4
    let blocks
    if (rg.custom) {
      const actorChips = filters.actors.map(a => ({
        groupId: rg.id, stateKey: 'actors', value: a.id,
        label: truncate(a.name), full: a.name, description: '',
        color: rg.color, icon: null,
      }))
      const positionChips = []
      filters.positions.forEach(id => {
        const grp = positionGroupById(id)
        positionChips.push(makeChip(rg, 'positions', id, grp,
          { label: truncate(grp?.name ?? `#${id}`) }))
      })
      Object.entries(filters.positionTypes).forEach(([gid, ids]) =>
        (ids || []).forEach(id => {
          const pt = positionTypeById(Number(gid), id)
          positionChips.push(makeChip(rg, 'positionTypes', id, pt,
            { label: truncate(pt?.name ?? `#${id}`), subGroupId: Number(gid) }))
        }))
      // Dos bandas solo si ambos tipos están activos; si no, una sola.
      blocks = (actorChips.length && positionChips.length)
        ? [actorChips, positionChips]
        : [actorChips.concat(positionChips)]
    } else {
      const chips = []
      rg.selects.forEach(sel => {
        const opts = optionsFor(rg.id, sel.stateKey)
        ;(filters[sel.stateKey] || []).forEach(id => {
          // Megaproyecto: color por su tipo de extractivismo (no por el nodo).
          const extra = rg.id === 'megaproject'
            ? { kind: 'megaproject', color: resolveExtractivism(id).color }
            : {}
          chips.push(makeChip(rg, sel.stateKey, id, opts.find(o => o.id === id),
            extra))
        })
      })
      if (rg.purposeKey)
        (filters[rg.purposeKey] || []).forEach(id => chips.push(makeChip(
          rg, rg.purposeKey, id, purposeOptions.value.find(o => o.id === id))))
      blocks = [chips]
    }
    return {
      id: rg.id, label: rg.label, icon: rg.icon, color: rg.color,
      maxCells, blocks,
    }
  }))

  // Total de chips de un grupo (todos sus bloques) para el badge del rail.
  const chipCount = g => g.blocks.reduce((n, b) => n + b.length, 0)

  // Conteo por grupo para el badge del rail (Capa A).
  const countFor = id => {
    const g = capsulesByGroup.value.find(g => g.id === id)
    return g ? chipCount(g) : 0
  }

  // ¿Hay algún filtro activo? Controla la Capa B y "limpiar todo".
  const hasActiveFilters = computed(() =>
    capsulesByGroup.value.some(g => chipCount(g) > 0))

  // ¿Algún grupo muestra dos chips lado a lado? (un bloque con ≥3 chips, que
  // es cuando la cuadrícula coloca 2 en una fila). Controla si tiene sentido
  // ofrecer "comprimir etiquetas".
  const anyAdjacentChips = computed(() =>
    capsulesByGroup.value.some(g => g.blocks.some(b => b.length >= 3)))

  // Quita un valor concreto de un filtro (cerrar un chip).
  function removeCapsule(cap) {
    if (cap.stateKey === 'actors')
      filters.actors = filters.actors.filter(a => a.id !== cap.value)
    else if (cap.stateKey === 'positionTypes')
      filters.positionTypes[cap.subGroupId] =
        (filters.positionTypes[cap.subGroupId] || [])
          .filter(v => v !== cap.value)
    else if (Array.isArray(filters[cap.stateKey]))
      filters[cap.stateKey] = filters[cap.stateKey].filter(v => v !== cap.value)
  }

  // Vacía todos los filtros de golpe (decisions §4 "limpiar todo").
  // Genérico: arrays → [], objetos (positionTypes) → {}.
  function clearAllFilters() {
    Object.keys(filters).forEach(k => {
      filters[k] = Array.isArray(filters[k]) ? [] : {}
    })
  }

  // Payload listo para el backend (punto de integración de filtros).
  // Hoy solo `extractivism` se aplica de verdad (useLayers); el resto se
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

  // Carga diferida del payload de facetas + construcción del índice invertido.
  // Idempotente: una sola vez por sesión. Se dispara tras el primer pintado.
  async function ensureFacets() {
    if (facetsReady.value) return
    const data = await mainStore.fetchProjectFacets()
    if (!data?.facets) return
    facetIndex.value = buildFacetIndex(data.facets)
    facetsReady.value = true
  }

  // Carga lazy del payload de actores + construcción de índices (invertido para
  // filtrar, MiniSearch para buscar). Idempotente: `actorsReady` corta tras la
  // primera vez; `actorsPromise` comparte una descarga en vuelo entre llamadas
  // concurrentes (buscador + picker) para no reconstruir dos veces.
  async function ensureActors() {
    if (actorsReady.value) return
    if (actorsPromise) return actorsPromise
    actorsPromise = (async () => {
      const data = await mainStore.fetchMapActors()
      if (!data?.actors) return
      const byId = new Map()
      for (const a of data.actors) byId.set(a.id, a)
      actorsById.value = byId
      // actor_projects llega keyed por string → Number; arrays → Set.
      const ap = new Map()
      for (const [actorId, projIds] of Object.entries(data.actor_projects || {}))
        ap.set(Number(actorId), new Set(projIds))
      actorProjects.value = ap
      actorSearchIndex.value = buildActorIndex(data.actors)
      actorsReady.value = true
      // Nombres reales para los actores hidratados desde la URL.
      reconcileActorNames()
    })()
    try { await actorsPromise } finally { actorsPromise = null }
  }

  // Remapea `filters.actors` con el nombre real de cada actor (los hidratados
  // desde la URL llegan como "Actor #id"). La URL no cambia: serialize() usa
  // solo el id; los chips leen `a.name` → se actualizan solos. Reasignar el
  // array dispara la reactividad de los chips.
  function reconcileActorNames() {
    if (!actorsById.value || !filters.actors.length) return
    filters.actors = filters.actors.map(a => {
      const real = actorsById.value.get(a.id)
      return real ? { id: a.id, name: real.name } : a
    })
  }

  // Índice de proyectos para el buscador global: se construye una sola vez, al
  // primer geojson cargado. `immediate` cubre el caso de que ya haya datos.
  watch(uniqueProjects, projects => {
    if (projects.length && !projectSearchIndex.value)
      projectSearchIndex.value = buildProjectIndex(projects)
  }, { immediate: true })

  const searchProjects = q => runSearch(projectSearchIndex.value, q)
  const searchActors = q => runSearch(actorSearchIndex.value, q)

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
    ensureFacets,
    facetsReady,
    ensureActors,
    actorsReady,
    actorsById,
    searchProjects,
    searchActors,
    visibleProjectIds,
    // --- Filtros ---
    filters,
    activePickerKey,
    railExpanded,
    chipsCompact,
    toggleRailExpanded,
    toggleChipsCompact,
    FILTER_REGISTRY,
    resolveGroup,
    optionsFor,
    purposeOptions,
    positionGroups,
    positionTypeOptions,
    // Cápsulas / conteo
    capsulesByGroup,
    countFor,
    hasActiveFilters,
    anyAdjacentChips,
    removeCapsule,
    clearAllFilters,
    filterPayload,
  }
})