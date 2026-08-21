import {storeToRefs} from 'pinia'
import {useMainStore} from '~/store/index.js'

/**
 * Centro de respaldo para abrir el mapa de una ubicación todavía sin
 * geometría: la localidad si la hay, y si no el municipio.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useClosePosition(full_main) {
  const {full_geo} = storeToRefs(useMainStore())

  return computed(() => {
    let close_position = null
    if (full_geo.value.municipality && full_main.value.locality) {
      const mun = full_geo.value.municipality[full_main.value.municipality]
      if (mun)
        close_position = mun.find(
          loc => loc.id === full_main.value.locality)
    }
    if (close_position)
      return close_position
    if (full_geo.value.state && full_main.value.municipality) {
      const state = full_geo.value.state[full_main.value.state]
      if (state) {
        close_position = state.find(
          mun => mun.id === full_main.value.municipality)
      }
    }
    return close_position || null
  })
}
