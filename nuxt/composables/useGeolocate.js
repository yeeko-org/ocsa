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

/**
 * Sugerencia de estado, municipio y localidad a partir de las coordenadas de
 * un punto. A diferencia del servidor, que sólo llena lo vacío, aquí se
 * sobrescribe lo ya elegido y por eso hay que avisarle al usuario.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useGeolocate(full_main) {
  const geo_store = useGeoNewStore()

  const notices = ref([])
  let timer = null
  // Lo último que puso la sugerencia: si los selectores ya no coinciden es
  // que el usuario los movió a mano y los avisos dejaron de describirlos.
  let last_suggested = null
  // Mientras se asignan los tres ids el watch vería cambios propios
  let applying = false

  function clear() {
    notices.value = []
    last_suggested = null
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

  return {notices, suggest, clear}
}
