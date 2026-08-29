import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest'
import {nextTick, ref} from 'vue'
import {createPinia, setActivePinia} from 'pinia'
import {geoService} from '~/services/geo.service.js'
import {useGeoNewStore} from '~/store/geo.js'
import {buildAlertComment, useGeolocate} from '~/composables/useGeolocate.js'

vi.mock('~/services/geo.service.js', () => ({
  geoService: {
    geolocate: vi.fn(),
    geolocateGeometry: vi.fn(),
  },
}))

const DEBOUNCE_MS = 400

const STATE_ID = 1
const MUNICIPALITY_ID = 10

const SUGGESTED_MUNICIPALITIES = [{id: 20, name: 'M', state: 2}]
const TOUCHED_LOCALITIES = [{id: 300, name: 'L', municipality: 20}]

// Ocho candidatas ordenadas por distancia: la octava está en la lista que
// decide los avisos, pero fuera de las seis que se muestran.
const DISTANCES = [0.4, 1.2, 2.3, 3.7, 4.2, 5.8, 6.5, 7.9]

const MANY_LOCALITIES = DISTANCES.map((distance_km, i) => ({
  id: 400 + i,
  name: `L${i + 1}`,
  distance_km,
  point: [-103.3 + i / 100, 20.6],
  municipality: 20,
}))

const MANY_RESPONSE = {
  data: {
    state: {id: 2, name: 'B'},
    municipality: {id: 20, name: 'M'},
    municipalities: SUGGESTED_MUNICIPALITIES,
    localities: MANY_LOCALITIES,
  },
}

const GEOMETRY_RESPONSE = {
  data: {
    state: {id: 2, name: 'B'},
    municipality: {id: 20, name: 'M'},
    locality: {id: 300, name: 'L'},
    municipalities: SUGGESTED_MUNICIPALITIES,
    localities: TOUCHED_LOCALITIES,
  },
}

const FEATURE = {
  type: 'Feature',
  geometry: {type: 'LineString', coordinates: [[-103.3, 20.6], [-103.1, 20.8]]},
}

// El setTimeout dispara una cadena async que nadie espera: hay que dejar
// correr los microtasks de `runSuggest*` y de cada `nextTick` interno.
async function runDebounce() {
  await vi.advanceTimersByTimeAsync(DEBOUNCE_MS)
  for (let i = 0; i < 5; i++) await nextTick()
}

describe('useGeolocate', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    vi.mocked(geoService.geolocateGeometry).mockResolvedValue(
        GEOMETRY_RESPONSE)
    vi.mocked(geoService.geolocate).mockResolvedValue(GEOMETRY_RESPONSE)
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('suggestGeometry sólo previsualiza los municipios atravesados',
      async () => {
        const full_main = ref({
          state: STATE_ID,
          municipality: null,
          locality: null,
          municipalities_full: [],
        })
        const {notices, suggestGeometry} = useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(geoService.geolocateGeometry).toHaveBeenCalledTimes(1)
        expect(geoService.geolocateGeometry).toHaveBeenCalledWith(
            FEATURE, STATE_ID)
        // Ni siquiera los campos vacíos se llenan: los escribe el
        // servidor al guardar, con el trazo ya completo.
        expect(full_main.value.state).toBe(STATE_ID)
        expect(full_main.value.municipality).toBeNull()
        expect(full_main.value.locality).toBeNull()
        expect(full_main.value.municipalities_full)
            .toEqual(SUGGESTED_MUNICIPALITIES)
        expect(notices.value).toEqual([])
      })

  it('suggestGeometry(null) cancela lo pendiente y vacía los municipios',
      async () => {
        const full_main = ref({
          state: STATE_ID,
          municipality: MUNICIPALITY_ID,
          locality: null,
          municipalities_full: SUGGESTED_MUNICIPALITIES,
        })
        const {suggestGeometry} = useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await vi.advanceTimersByTimeAsync(DEBOUNCE_MS - 100)
        suggestGeometry(null)
        await runDebounce()

        expect(geoService.geolocateGeometry).not.toHaveBeenCalled()
        expect(full_main.value.municipalities_full).toEqual([])
      })

  it('avisa del municipio capturado fuera del trazo y lo retira al '
      + 'corregirlo', async () => {
        const full_main = ref({
          state: STATE_ID,
          // No está entre los municipios que devuelve el trazo.
          municipality: MUNICIPALITY_ID,
          locality: null,
          municipalities_full: [],
        })
        const {warnings, suggestGeometry} = useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(warnings.value).toHaveLength(1)
        expect(warnings.value[0]).toContain(
            'no está entre los que atraviesa el trazo')

        // El catálogo no está cargado en el store: el aviso sale sin
        // nombrar al municipio.
        expect(warnings.value[0]).not.toContain('(')

        full_main.value.municipality = SUGGESTED_MUNICIPALITIES[0].id
        await nextTick()

        expect(warnings.value).toEqual([])
      })

  it('avisa de la localidad capturada fuera de las cercanas',
      async () => {
    const full_main = ref({
      state: STATE_ID,
      municipality: SUGGESTED_MUNICIPALITIES[0].id,
      // No está entre las que el servidor devuelve a 5 km del trazo.
      locality: 999,
      municipalities_full: [],
    })
    const {warnings, suggestGeometry} = useGeolocate(full_main)

    suggestGeometry(FEATURE)
    await runDebounce()

    expect(warnings.value).toHaveLength(1)
    expect(warnings.value[0]).toContain(
        'no está entre las cercanas a los municipios que atraviesa el trazo')

    full_main.value.locality = TOUCHED_LOCALITIES[0].id
    await nextTick()

    expect(warnings.value).toEqual([])
  })

  it('suggest (punto) sobrescribe y avisa del cambio', async () => {
    const geo_store = useGeoNewStore()
    geo_store.states = [{id: STATE_ID, name: 'A', short_name: 'A'}]
    const full_main = ref({
      state: STATE_ID,
      municipality: MUNICIPALITY_ID,
      locality: null,
    })
    const {notices, suggest} = useGeolocate(full_main)

    suggest(20.6, -103.3)
    await runDebounce()

    expect(geoService.geolocate).toHaveBeenCalledWith(20.6, -103.3, STATE_ID)
    expect(full_main.value.state).toBe(2)
    expect(full_main.value.municipality).toBe(20)
    expect(full_main.value.locality).toBe(300)
    // La localidad estaba vacía: sólo estado y municipio cambiaron de valor.
    expect(notices.value).toHaveLength(2)
    expect(notices.value[0]).toContain('de A a B')
  })

  it('decide el aviso con la lista completa, no con las seis mostradas',
      async () => {
        vi.mocked(geoService.geolocateGeometry).mockResolvedValue(
            MANY_RESPONSE)
        const far = MANY_LOCALITIES[MANY_LOCALITIES.length - 1]
        const full_main = ref({
          state: STATE_ID,
          municipality: SUGGESTED_MUNICIPALITIES[0].id,
          // Está en la lista, pero no entre las seis que se muestran
          locality: far.id,
          municipalities_full: [],
        })
        const {warnings, candidates, suggestGeometry} = useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(warnings.value).toEqual([])
        expect(candidates.value).toHaveLength(6)
        expect(candidates.value.map(item => item.id))
            .not.toContain(far.id)
      })

  it('arma las candidatas con nombre, distancia y punto', async () => {
    vi.mocked(geoService.geolocateGeometry).mockResolvedValue(MANY_RESPONSE)
    const full_main = ref({
      state: STATE_ID,
      municipality: null,
      locality: null,
      municipalities_full: [],
    })
    const {candidates, candidates_text, suggestGeometry} =
        useGeolocate(full_main)

    suggestGeometry(FEATURE)
    await runDebounce()

    expect(candidates.value[0].label).toBe('L1 (0.4 km)')
    expect(candidates.value[0].point).toEqual(MANY_LOCALITIES[0].point)
    expect(candidates.value[5].label).toBe('L6 (5.8 km)')
    expect(candidates_text.value).toBe(
        'Localidades cercanas: L1 (0.4 km), L2 (1.2 km), L3 (2.3 km), '
        + 'L4 (3.7 km), L5 (4.2 km), L6 (5.8 km).')

    // Cambiar la geometría retira las candidatas antes de la respuesta nueva
    suggestGeometry(null)
    expect(candidates.value).toEqual([])
    expect(candidates_text.value).toBe('')
  })

  it('no ofrece candidatas cuando el servidor devuelve una sola',
      async () => {
        const full_main = ref({
          state: STATE_ID,
          municipality: null,
          locality: null,
          municipalities_full: [],
        })
        const {candidates, candidates_text, suggestGeometry} =
            useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(candidates.value).toEqual([])
        expect(candidates_text.value).toBe('')
      })

  it('el pin también trae candidatas y avisa con el texto del punto',
      async () => {
        vi.mocked(geoService.geolocate).mockResolvedValue({
          data: {...MANY_RESPONSE.data, locality: null},
        })
        const full_main = ref({
          state: STATE_ID,
          municipality: MUNICIPALITY_ID,
          // El motor no elige localidad: la capturada sigue ahí y no está
          // entre las cercanas al municipio del pin.
          locality: 999,
          municipalities_full: [],
        })
        const {warnings, candidates, suggest} = useGeolocate(full_main)

        suggest(20.6, -103.3)
        await runDebounce()

        expect(candidates.value).toHaveLength(6)
        expect(warnings.value).toHaveLength(1)
        expect(warnings.value[0]).toContain(
            'no está entre las cercanas al municipio del pin')
      })

  it('el reemplazo automático sobrescribe, borra lo no resuelto y se '
      + 'deshace', async () => {
        vi.mocked(geoService.geolocateGeometry).mockResolvedValue({
          // El motor resolvió estado y municipio, pero ninguna localidad
          data: {...MANY_RESPONSE.data, locality: null},
        })
        const full_main = ref({
          state: STATE_ID,
          municipality: MUNICIPALITY_ID,
          locality: 999,
          municipalities_full: [],
        })
        const {can_replace, has_replacement, replaceAll, undoReplace,
          suggestGeometry} = useGeolocate(full_main)

        expect(can_replace.value).toBe(false)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(can_replace.value).toBe(true)
        expect(has_replacement.value).toBe(false)

        await replaceAll()

        expect(full_main.value.state).toBe(2)
        expect(full_main.value.municipality).toBe(20)
        // Lo que el motor no resolvió se borra: ése es el punto del botón
        expect(full_main.value.locality).toBeNull()
        expect(full_main.value.municipalities_full)
            .toEqual(SUGGESTED_MUNICIPALITIES)
        expect(has_replacement.value).toBe(true)

        await undoReplace()

        expect(full_main.value.state).toBe(STATE_ID)
        expect(full_main.value.municipality).toBe(MUNICIPALITY_ID)
        expect(full_main.value.locality).toBe(999)
        // La tira de municipios atravesados no se deshace: es un derivado
        // del trazo, que no cambió.
        expect(full_main.value.municipalities_full)
            .toEqual(SUGGESTED_MUNICIPALITIES)
        expect(has_replacement.value).toBe(false)
      })

  it('no ofrece el reemplazo cuando el motor no resolvió nada',
      async () => {
        vi.mocked(geoService.geolocateGeometry).mockResolvedValue({
          data: {state: null, municipality: null, locality: null,
            municipalities: [], localities: []},
        })
        const full_main = ref({
          state: STATE_ID,
          municipality: MUNICIPALITY_ID,
          locality: null,
          municipalities_full: [],
        })
        const {can_replace, suggestGeometry} = useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()

        expect(geoService.geolocateGeometry).toHaveBeenCalledTimes(1)
        expect(can_replace.value).toBe(false)
      })

  it('una geometría nueva descarta el deshacer del reemplazo anterior',
      async () => {
        const full_main = ref({
          state: STATE_ID,
          municipality: MUNICIPALITY_ID,
          locality: null,
          municipalities_full: [],
        })
        const {has_replacement, replaceAll, suggestGeometry} =
            useGeolocate(full_main)

        suggestGeometry(FEATURE)
        await runDebounce()
        await replaceAll()
        expect(has_replacement.value).toBe(true)

        suggestGeometry(FEATURE)
        expect(has_replacement.value).toBe(false)
      })

  describe('buildAlertComment', () => {
    beforeEach(() => vi.setSystemTime(new Date('2026-08-29T10:00:00')))

    it('inicia los comentarios con fecha, autor y el aviso en minúscula',
        () => {
          const text = 'La localidad capturada (X) no está entre las '
              + 'cercanas al municipio del pin.'
          expect(buildAlertComment('', text, 'Ricardo')).toBe(
              '29/08/2026 - Ricardo: la localidad capturada (X) no está '
              + 'entre las cercanas al municipio del pin.')
        })

    it('separa del comentario previo con un renglón en blanco', () => {
      expect(buildAlertComment('Anterior', 'Aviso.', 'Ricardo')).toBe(
          'Anterior\n\n29/08/2026 - Ricardo: aviso.')
    })
  })
})
