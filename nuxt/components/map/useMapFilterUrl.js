import _debounce from "lodash/debounce.js";
import { useMapStore } from "~/store/map.js";

// Sincroniza el estado de filtros con los query params de la URL para que una
// vista filtrada sea compartible/recuperable por link (decisions §15).
//
// Formato: cada filtro de array → CSV de ids (`extractivism=1,2`). Las
// sub-posiciones (objeto {grupo: [ids]}) → `positionTypes=1:4.5;2:7`. Los
// actores guardan solo el id (su nombre vive en /actor/, fuera de cats); al
// hidratar desde la URL mostramos "Actor #id" hasta el cableado de Sesión 4.

// Filtros que son arrays simples de ids.
const ARRAY_KEYS = [
  'extractivism', 'megaproject', 'violence', 'collectiveActions', 'legal',
  'legalPurpose', 'socialImpacts', 'environmentalImpacts', 'states',
]

export function useMapFilterUrl() {
  const route = useRoute()
  const router = useRouter()
  const mapStore = useMapStore()
  const { filters } = mapStore

  // filters → objeto query (omitiendo lo vacío).
  function serialize() {
    const query = {}
    ARRAY_KEYS.forEach(k => {
      if (filters[k].length) query[k] = filters[k].join(',')
    })
    if (filters.actors.length)
      query.actors = filters.actors.map(a => a.id).join(',')
    if (filters.positions.length)
      query.positions = filters.positions.join(',')
    const ptEntries = Object.entries(filters.positionTypes)
      .filter(([, ids]) => ids?.length)
    if (ptEntries.length)
      query.positionTypes = ptEntries
        .map(([g, ids]) => `${g}:${ids.join('.')}`).join(';')
    return query
  }

  // query → filters (al cargar la página).
  function hydrate() {
    const q = route.query
    ARRAY_KEYS.forEach(k => {
      filters[k] = q[k] ? String(q[k]).split(',').map(Number) : []
    })
    filters.actors = q.actors
      ? String(q.actors).split(',')
          .map(id => ({ id: Number(id), name: `Actor #${id}` }))
      : []
    filters.positions = q.positions
      ? String(q.positions).split(',').map(Number) : []
    const pt = {}
    if (q.positionTypes) {
      String(q.positionTypes).split(';').forEach(chunk => {
        const [g, ids] = chunk.split(':')
        if (g && ids) pt[Number(g)] = ids.split('.').map(Number)
      })
    }
    filters.positionTypes = pt
  }

  const pushQuery = _debounce(() => {
    router.replace({ query: serialize() })
  }, 400)

  // Orden importante: hidratamos ANTES de observar, así las asignaciones de
  // hydrate() no disparan pushQuery (no se reescribe la URL recién leída).
  hydrate()
  watch(filters, pushQuery, { deep: true })
}
