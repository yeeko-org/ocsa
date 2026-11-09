// Búsqueda local de GenericSelect, aparte del componente para probarla sin
// montar Vuetify.

import {foldText} from '~/composables/foldText.js'

// alternative_names (autónimos, grafías) cuenta como nombre: buscar
// «Wixárika» tiene que encontrar «Huichol» aunque se llame de otra forma.
export const itemNames = (raw, item_title = 'name') =>
  foldText(`${raw[item_title] || ''} ${raw.alternative_names || ''}`)

export function matchesSearch(raw, query, item_title = 'name') {
  if (!query) return true
  const folded = foldText(query)
  return itemNames(raw, item_title).includes(folded)
    || foldText(raw.description).includes(folded)
}

// Primero lo que coincide por nombre, luego por descripción; el sort es
// estable, así que dentro de cada grupo se respeta el orden original.
export function sortBySearch(items, query, item_title = 'name') {
  const folded = foldText(query)
  const rank = (raw) => {
    if (itemNames(raw, item_title).includes(folded)) return 0
    if (foldText(raw.description).includes(folded)) return 1
    return 2
  }
  return [...items].sort((a, b) => rank(a) - rank(b))
}
