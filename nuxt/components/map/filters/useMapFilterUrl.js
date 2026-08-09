import _debounce from "lodash/debounce.js";
import { useMapStore } from "~/store/map.js";
import { FILTER_REGISTRY } from "~/components/map/filters/filterRegistry.js";

// Sincroniza el estado de filtros con los query params de la URL para que una
// vista filtrada sea compartible/recuperable por link (decisions §15).
//
// Formato: cada filtro → CSV de ids (`extractivism=1,2`). Los actores guardan
// solo el id (su nombre vive en /actor/, fuera de cats); al hidratar desde la
// URL mostramos "Actor #id" como marcador.

// Filtros que son arrays simples de ids, derivados del registro: todos los
// stateKeys de los selects (incluye los subtipos de afectación) + el
// purposeKey de legal. `extractivism` se elige en la leyenda (no es un select
// del registro), pero sigue siendo un filtro array → se añade a mano.
// Actores/posiciones se serializan aparte (abajo).
const ARRAY_KEYS = [
  'extractivism',
  ...FILTER_REGISTRY.flatMap(g => (g.selects || []).map(s => s.stateKey)),
  ...FILTER_REGISTRY.filter(g => g.purposeKey).map(g => g.purposeKey),
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
  }

  const pushQuery = _debounce(() => {
    router.replace({ query: serialize() })
  }, 400)

  // Orden importante: hidratamos ANTES de observar, así las asignaciones de
  // hydrate() no disparan pushQuery (no se reescribe la URL recién leída).
  hydrate()
  watch(filters, pushQuery, { deep: true })
}
