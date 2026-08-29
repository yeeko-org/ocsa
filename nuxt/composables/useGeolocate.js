import {nextTick, ref, watch} from 'vue'
import {geoService} from '~/services/geo.service.js'
import {useGeoNewStore} from '~/store/geo.js'

const DEBOUNCE_MS = 400

// Dos variantes por campo: cuando el catálogo no tiene cargado el nombre
// previo, el aviso sólo puede decir en qué quedó el campo.
const FIELD_NOTICES = {
  state: {
    changed: (from, to) =>
        `Se cambió el Estado según las coordenadas: de ${from} a ${to}.`,
    set: to => `Se cambió el Estado según las coordenadas: ahora es ${to}.`,
  },
  municipality: {
    changed: (from, to) =>
        `Se cambió el Municipio según las coordenadas: de ${from} a ${to}.`,
    set: to => `Se cambió el Municipio según las coordenadas: ahora es ${to}.`,
  },
  locality: {
    changed: (from, to) =>
        `Se cambió la Localidad según las coordenadas: de ${from} a ${to}.`,
    set: to => `Se cambió la Localidad según las coordenadas: ahora es ${to}.`,
  },
}

// Los nombres salen del catálogo ya cargado en el store; sin él el aviso
// sigue valiendo, sólo que sin nombrar lo capturado.
const named = name => name ? ` (${name})` : ''

// La tolerancia de la localidad la aplica el servidor al armar la lista
// (`LOCALITY_TOLERANCE_M`); aquí sólo se nombra, para que el aviso diga
// por qué salió.
const LOCALITY_TOLERANCE_KM = 5

const GEOMETRY_WARNINGS = {
  municipality: name => `El municipio capturado${named(name)} no está `
      + `entre los que atraviesa el trazo.`,
  locality: name => `La localidad capturada${named(name)} está a más de `
      + `${LOCALITY_TOLERANCE_KM} km del trazo.`,
}

/**
 * Sugerencia de estado, municipio y localidad a partir de la geometría.
 *
 * `suggest` (punto) sobrescribe lo ya elegido —la excepción documentada al
 * criterio del motor— y por eso avisa al usuario; `suggestGeometry` (línea o
 * polígono) no toca los selectores, porque un trazo se edita por tramos y la
 * sugerencia calculada sobre uno parcial se quedaría pegada: el servidor los
 * llena al guardar, con el trazo ya completo. A cambio contrasta lo capturado
 * contra el trazo y deja en `warnings` lo que no cuadra, sin bloquear nada.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useGeolocate(full_main) {
  const geo_store = useGeoNewStore()

  const notices = ref([])
  const warnings = ref([])
  let timer = null
  // Última respuesta del trazo: los avisos se recalculan contra ella al
  // corregir un selector, sin volver a preguntarle al servidor.
  let last_geometry = null
  // Lo último que puso la sugerencia: si los selectores ya no coinciden es
  // que el usuario los movió a mano y los avisos dejaron de describirlos.
  let last_suggested = null
  // Mientras se asignan los tres ids el watch vería cambios propios
  let applying = false

  function clear() {
    notices.value = []
    warnings.value = []
    last_suggested = null
    last_geometry = null
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  function stateName(state_id) {
    const state = geo_store.states.find(item => item.id === state_id)
    return state?.short_name || state?.name || null
  }

  function municipalityName(state_id, municipality_id) {
    const municipalities = geo_store.states_full[state_id] || []
    const found = municipalities.find(item => item.id === municipality_id)
    return found?.name || null
  }

  function localityName(municipality_id, locality_id) {
    const localities = geo_store.municipalities_full[municipality_id] || []
    const found = localities.find(item => item.id === locality_id)
    return found?.name || null
  }

  function previousNames(previous) {
    return {
      state: stateName(previous.state),
      municipality: municipalityName(previous.state, previous.municipality),
      locality: localityName(previous.municipality, previous.locality),
    }
  }

  function addNotice(field, previous_id, previous_name, suggested) {
    if (!previous_id || previous_id === suggested.id) return
    const notice = FIELD_NOTICES[field]
    notices.value.push(previous_name
        ? notice.changed(previous_name, suggested.name)
        : notice.set(suggested.name))
  }

  async function applySuggestion(data) {
    const loc = full_main.value
    const previous = {
      state: loc.state,
      municipality: loc.municipality,
      locality: loc.locality,
    }
    const names = previousNames(previous)

    applying = true
    // El orden importa: los watch de LocationMex anulan municipio y
    // localidad al cambiar el estado, y localidad al cambiar el municipio.
    if (data.state) {
      addNotice('state', previous.state, names.state, data.state)
      loc.state = data.state.id
      await nextTick()
    }
    if (data.municipality) {
      addNotice('municipality', previous.municipality, names.municipality,
          data.municipality)
      loc.municipality = data.municipality.id
      await nextTick()
    }
    if (data.locality) {
      addNotice('locality', previous.locality, names.locality, data.locality)
      loc.locality = data.locality.id
    }
    last_suggested = {
      state: loc.state,
      municipality: loc.municipality,
      locality: loc.locality,
    }
    await nextTick()
    applying = false
  }

  function inResponse(list, id) {
    // Una respuesta sin la lista no es una lista vacía: no se avisa de
    // lo que el servidor no informó.
    if (!Array.isArray(list)) return true
    return list.some(item => item.id === id)
  }

  // Contra lo que se enviaría, no contra lo guardado: el aviso tiene que
  // salir antes de guardar y desaparecer en cuanto se corrige el selector.
  function checkGeometry() {
    warnings.value = []
    const loc = full_main.value
    if (!last_geometry || !loc) return
    if (loc.municipality
        && !inResponse(last_geometry.municipalities, loc.municipality))
      warnings.value.push(GEOMETRY_WARNINGS.municipality(
          municipalityName(loc.state, loc.municipality)))
    if (loc.locality
        && !inResponse(last_geometry.localities, loc.locality))
      warnings.value.push(GEOMETRY_WARNINGS.locality(
          localityName(loc.municipality, loc.locality)))
  }

  async function runSuggestGeometry(feature) {
    const response = await geoService.geolocateGeometry(
        feature, full_main.value.state)
    const data = response?.data
    if (!data) return
    notices.value = []
    // Vista previa de la franja: LocationMunicipalities muestra los
    // municipios atravesados antes de guardar.
    full_main.value.municipalities_full = data.municipalities || []
    last_geometry = data
    checkGeometry()
  }

  function suggestGeometry(feature) {
    if (timer) clearTimeout(timer)
    if (!feature) {
      timer = null
      last_geometry = null
      warnings.value = []
      if (full_main.value) full_main.value.municipalities_full = []
      return
    }
    timer = setTimeout(() => {
      timer = null
      runSuggestGeometry(feature)
    }, DEBOUNCE_MS)
  }

  async function runSuggest(lat, lon) {
    const response = await geoService.geolocate(
        lat, lon, full_main.value.state)
    const data = response?.data
    if (!data) return
    notices.value = []
    await applySuggestion(data)
  }

  function suggest(lat, lon) {
    if (timer) clearTimeout(timer)
    if (!lat || !lon) return
    timer = setTimeout(() => {
      timer = null
      runSuggest(lat, lon)
    }, DEBOUNCE_MS)
  }

  watch(
      () => [full_main.value?.state, full_main.value?.municipality,
        full_main.value?.locality],
      ([state, municipality, locality]) => {
        if (applying || !last_suggested) return
        if (state === last_suggested.state
            && municipality === last_suggested.municipality
            && locality === last_suggested.locality) return
        clear()
      })

  watch(
      () => [full_main.value?.municipality, full_main.value?.locality],
      () => checkGeometry())

  return {notices, warnings, suggest, suggestGeometry, clear}
}
