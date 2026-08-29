import {computed, nextTick, ref, watch} from 'vue'
import dayjs from 'dayjs'
import {geoService} from '~/services/geo.service.js'
import {useGeoNewStore} from '~/store/geo.js'

const DEBOUNCE_MS = 400

// Cuántas localidades candidatas se muestran; la decisión de los avisos usa
// siempre la lista completa que mandó el servidor.
const MAX_SHOWN_LOCALITIES = 6

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

// La lista de localidades viene acotada a los municipios de la geometría, así
// que la ausencia sólo prueba eso: no dice a qué distancia quedó lo capturado.
const GEOMETRY_WARNINGS = {
  municipality: name => `El municipio capturado${named(name)} no está `
      + `entre los que atraviesa el trazo.`,
  locality: {
    geometry: name => `La localidad capturada${named(name)} no está entre `
        + `las cercanas a los municipios que atraviesa el trazo.`,
    point: name => `La localidad capturada${named(name)} no está entre `
        + `las cercanas al municipio del pin.`,
  },
}

function candidateLabel(item) {
  return `${item.name} (${Number(item.distance_km).toFixed(1)} km)`
}

/**
 * Texto de un aviso convertido en comentario, con la convención de
 * `Comments.vue`: separador de párrafo, fecha y autor. Vive aquí porque el
 * texto del aviso es de este módulo y así se prueba sin montar el componente.
 *
 * @param {string} comments comentarios actuales de la ubicación
 * @param {string} text aviso tal como se muestra
 * @param {string} user_name nombre de pila del editor
 */
export function buildAlertComment(comments, text, user_name) {
  const previous = comments ? `${comments}\n\n` : ''
  const today = dayjs().format('DD/MM/YYYY')
  // Minúscula inicial para encadenar con el prefijo, como los comentarios
  // que escribe el servidor.
  const body = text.charAt(0).toLowerCase() + text.slice(1)
  return `${previous}${today} - ${user_name}: ${body}`
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
 * `replaceAll` es el tercer camino, explícito: aplica la resolución completa
 * del motor sobre los cuatro campos, borrando lo que el motor no resolvió.
 *
 * @param {Ref<Object>} full_main modelo de la ubicación
 */
export function useGeolocate(full_main) {
  const geo_store = useGeoNewStore()

  const notices = ref([])
  const warnings = ref([])
  // Última respuesta del motor: los avisos se recalculan contra ella al
  // corregir un selector, sin volver a preguntarle al servidor.
  const last_response = ref(null)
  // Valores previos al reemplazo automático, para deshacerlo
  const replaced = ref(null)
  let last_source = null
  let timer = null
  // Lo último que puso la sugerencia: si los selectores ya no coinciden es
  // que el usuario los movió a mano y los avisos dejaron de describirlos.
  let last_suggested = null
  // Mientras se asignan los tres ids el watch vería cambios propios
  let applying = false

  const localities = computed(() => {
    const list = last_response.value?.localities
    return Array.isArray(list) ? list : []
  })

  // Una sola candidata no es una elección que mostrar: o el motor ya la
  // escribió, o el aviso de localidad ya dice lo suyo.
  const candidates = computed(() => localities.value.length < 2 ? []
      : localities.value.slice(0, MAX_SHOWN_LOCALITIES).map(item => ({
        ...item, label: candidateLabel(item)
      })))

  const candidates_text = computed(() => candidates.value.length
      ? 'Localidades cercanas: '
          + `${candidates.value.map(item => item.label).join(', ')}.`
      : '')

  // Una respuesta que no resolvió nada no habilita el reemplazo: aplicarla
  // sólo borraría lo capturado, sin poner nada en su lugar.
  const can_replace = computed(() => {
    const data = last_response.value
    if (!data) return false
    return !!(data.state || data.municipality || data.locality
        || data.municipalities?.length)
  })
  const has_replacement = computed(() => !!replaced.value)

  // Lo que deja de valer en cuanto cambia la geometría
  function resetResolution() {
    last_response.value = null
    replaced.value = null
    last_source = null
    warnings.value = []
  }

  function clear() {
    notices.value = []
    last_suggested = null
    resetResolution()
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
    const localities_full = geo_store.municipalities_full[municipality_id] || []
    const found = localities_full.find(item => item.id === locality_id)
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
  function checkWarnings() {
    warnings.value = []
    const loc = full_main.value
    const data = last_response.value
    if (!data || !loc) return
    // El municipio sólo se contrasta con un trazo: para un pin el motor
    // resuelve uno y el M2M de atravesados viaja vacío.
    if (last_source === 'geometry' && loc.municipality
        && !inResponse(data.municipalities, loc.municipality))
      warnings.value.push(GEOMETRY_WARNINGS.municipality(
          municipalityName(loc.state, loc.municipality)))
    if (loc.locality && !inResponse(data.localities, loc.locality))
      warnings.value.push(GEOMETRY_WARNINGS.locality[last_source](
          localityName(loc.municipality, loc.locality)))
  }

  // Escribe los cuatro campos de golpe, con el mismo orden que la sugerencia
  // porque los watch de LocationMex encadenan los selectores.
  async function writeResolution(values) {
    const loc = full_main.value
    if (!loc) return
    applying = true
    loc.state = values.state
    await nextTick()
    loc.municipality = values.municipality
    await nextTick()
    loc.locality = values.locality
    loc.municipalities_full = values.municipalities_full || []
    await nextTick()
    if (last_suggested) last_suggested = {
      state: loc.state,
      municipality: loc.municipality,
      locality: loc.locality,
    }
    applying = false
    // Los avisos describían la sugerencia anterior, no lo recién escrito
    notices.value = []
    checkWarnings()
  }

  async function replaceAll() {
    const data = last_response.value
    const loc = full_main.value
    if (!data || !loc) return
    replaced.value = {
      state: loc.state,
      municipality: loc.municipality,
      locality: loc.locality,
      municipalities_full: loc.municipalities_full,
    }
    await writeResolution({
      state: data.state?.id || null,
      municipality: data.municipality?.id || null,
      locality: data.locality?.id || null,
      municipalities_full: data.municipalities || [],
    })
  }

  async function undoReplace() {
    if (!replaced.value) return
    const previous = replaced.value
    replaced.value = null
    await writeResolution(previous)
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
    last_response.value = data
    last_source = 'geometry'
    checkWarnings()
  }

  function suggestGeometry(feature) {
    if (timer) clearTimeout(timer)
    resetResolution()
    if (!feature) {
      timer = null
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
    last_response.value = data
    last_source = 'point'
    checkWarnings()
  }

  function suggest(lat, lon) {
    if (timer) clearTimeout(timer)
    resetResolution()
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
        // Mover un selector a mano invalida lo que dice haber sugerido el
        // pin, pero no la resolución: las candidatas y el reemplazo siguen
        // describiendo la geometría, que no cambió.
        notices.value = []
        last_suggested = null
      })

  watch(
      () => [full_main.value?.municipality, full_main.value?.locality],
      () => checkWarnings())

  return {
    notices,
    warnings,
    candidates,
    candidates_text,
    can_replace,
    has_replacement,
    suggest,
    suggestGeometry,
    replaceAll,
    undoReplace,
    clear,
  }
}
