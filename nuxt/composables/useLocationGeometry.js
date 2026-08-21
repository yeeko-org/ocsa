import {LOCATION_TYPES} from '~/composables/location_types.js'

/**
 * Reglas de la geometría de una ubicación según su tipo: el punto vive en
 * latitud/longitud y los demás tipos en geojson, así que cambiar de tipo
 * siempre deja datos huérfanos del tipo anterior.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useLocationGeometry(full_main) {

  function hasGeometry(type) {
    const loc = full_main.value
    if (type === 'point')
      return !!(loc.latitude && loc.longitude)
    return !!loc.geojson
  }

  // Limpia el campo que el tipo recibido no usa
  function clearOtherGeometry(type) {
    if (type === 'point') {
      full_main.value.geojson = null
    } else {
      full_main.value.latitude = null
      full_main.value.longitude = null
    }
  }

  // feature es null cuando se borran todas las figuras dibujadas
  function applyFeature(feature) {
    if (full_main.value.type_location === 'point') {
      const coords = feature?.geometry?.coordinates
      full_main.value.longitude = coords ? coords[0] : null
      full_main.value.latitude = coords ? coords[1] : null
    } else {
      full_main.value.geojson = feature
    }
  }

  function geometryParts() {
    const geojson = full_main.value.geojson
    if (!geojson) return 0
    if (geojson.type === 'FeatureCollection')
      return geojson.features.length
    const geometry = geojson.type === 'Feature' ? geojson.geometry : geojson
    if (!geometry?.type) return 0
    return geometry.type.startsWith('Multi') ? geometry.coordinates.length : 1
  }

  // Cómo nombrar en la interfaz lo que se va a perder
  function geometryLabel(type) {
    if (type === 'point') return 'las coordenadas capturadas'
    const type_full = LOCATION_TYPES.find(loc => loc.id === type)
    const parts = geometryParts()
    const name = parts === 1
        ? (type_full?.name || '').toLowerCase()
        : type_full?.name_plural
    return `la geometría capturada (${parts} ${name})`
  }

  return {hasGeometry, clearOtherGeometry, applyFeature, geometryLabel}
}
