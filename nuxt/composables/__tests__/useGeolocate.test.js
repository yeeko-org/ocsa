import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest'
import {nextTick, ref} from 'vue'
import {createPinia, setActivePinia} from 'pinia'
import {geoService} from '~/services/geo.service.js'
import {useGeoNewStore} from '~/store/geo.js'
import {useGeolocate} from '~/composables/useGeolocate.js'

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

  it('avisa de la localidad capturada lejos del trazo', async () => {
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
    expect(warnings.value[0]).toContain('está a más de 5 km del trazo')

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
})
