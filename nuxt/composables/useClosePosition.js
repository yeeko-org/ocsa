import {computed} from 'vue'
import {storeToRefs} from 'pinia'
import {useGeoNewStore} from '~/store/geo.js'

/**
 * Centro de respaldo para abrir el mapa de una ubicación todavía sin
 * geometría: la localidad si la hay, y si no la cabecera del municipio.
 *
 * El resultado no tiene forma única: quien lo consume distingue un municipio
 * de una localidad por la llave `state` o `municipality`.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useClosePosition(full_main) {
  const {states_full, municipalities_full} = storeToRefs(useGeoNewStore())

  // Sin coordenadas no sirve como centro y el mapa se rompería al volar
  function withCoords(place) {
    return place?.latitude && place?.longitude ? place : null
  }

  return computed(() => {
    const loc = full_main.value || {}
    let close_position = null
    if (loc.municipality && loc.locality) {
      const localities = municipalities_full.value[loc.municipality]
      if (localities)
        close_position = withCoords(
            localities.find(locality => locality.id === loc.locality))
    }
    if (close_position)
      return close_position
    if (loc.state && loc.municipality) {
      const municipalities = states_full.value[loc.state]
      if (municipalities)
        close_position = withCoords(
            municipalities.find(mun => mun.id === loc.municipality))
    }
    return close_position || null
  })
}
