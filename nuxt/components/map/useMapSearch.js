import MiniSearch from 'minisearch'

// Búsqueda 100% en cliente (api-contract "Búsqueda principal"): no hay
// endpoint server-side. Con los nombres de proyecto (geojson) y todos los
// actores (payload 3) en memoria, MiniSearch indexa ambas colecciones.
//
// Helpers sin estado: las INSTANCIAS del índice viven en el store
// (store/map.js, como shallowRef) para compartirse entre el buscador global
// y el de actores sin reconstruirlas por componente.

// Plegado de acentos + minúsculas, aplicado tanto al indexar como al buscar:
// "rio" debe encontrar "Río", "angel" → "Ángel". NFD separa la tilde en un
// diacrítico combinante (rango U+0300–U+036F) que se elimina.
export const processTerm = (term) =>
  term.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

// prefix: empareja por prefijo (búsqueda incremental al teclear).
// fuzzy 0.2: tolera ~20% de erratas por término.
const SEARCH_OPTS = { prefix: true, fuzzy: 0.2 }

// Etiqueta del proyecto, espejo de `searchableProjects` (store/map.js):
// incluye el nombre alternativo entre paréntesis cuando existe.
const projectLabel = (p) =>
  p.alternative_name ? `${p.name} (${p.alternative_name})` : p.name

// Índice de proyectos: busca por nombre y nombre alternativo; guarda lo
// necesario para pintar la opción sin volver al store.
export function buildProjectIndex(projects) {
  const index = new MiniSearch({
    fields: ['name', 'alternative_name'],
    storeFields: ['id', 'name', 'alternative_name'],
    processTerm,
  })
  index.addAll(projects.map(p => ({
    id: p.id,
    name: p.name,
    alternative_name: p.alternative_name || '',
  })))
  return index
}

// Índice de actores: solo por nombre.
export function buildActorIndex(actors) {
  const index = new MiniSearch({
    fields: ['name'],
    storeFields: ['id', 'name'],
    processTerm,
  })
  index.addAll(actors.map(a => ({ id: a.id, name: a.name })))
  return index
}

// Ejecuta la búsqueda y normaliza la salida a opciones { id, name, label }.
// Devuelve [] si no hay índice o query (estado inicial del autocomplete).
export function runSearch(index, query) {
  if (!index || !query) return []
  return index.search(query, SEARCH_OPTS).map(r => ({
    id: r.id,
    name: r.name,
    label: projectLabel(r),
  }))
}