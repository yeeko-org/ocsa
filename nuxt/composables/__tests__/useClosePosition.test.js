import {describe, expect, it, beforeEach} from 'vitest'
import {ref} from 'vue'
import {createPinia, setActivePinia} from 'pinia'
import {useGeoNewStore} from '~/store/geo.js'
import {useClosePosition} from '~/composables/useClosePosition.js'

const STATE_ID = 14
const MUNICIPALITY_ID = 120
const LOCALITY_ID = 5001

// Las llaves `state` y `municipality` son el discriminante del resultado:
// quitarlas del fixture volvería inútiles las aserciones de abajo.
const MUNICIPALITY = {
  id: MUNICIPALITY_ID,
  name: 'Guadalajara',
  state: STATE_ID,
  latitude: 20.6767,
  longitude: -103.3475,
}

const LOCALITY = {
  id: LOCALITY_ID,
  name: 'San Andrés',
  municipality: MUNICIPALITY_ID,
  latitude: 20.7101,
  longitude: -103.3011,
}

function fillCaches() {
  const geo_store = useGeoNewStore()
  geo_store.states_full[STATE_ID] = [MUNICIPALITY]
  geo_store.municipalities_full[MUNICIPALITY_ID] = [LOCALITY]
}

describe('useClosePosition', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fillCaches()
  })

  it('devuelve las coordenadas de la localidad cuando la hay', () => {
    const full_main = ref({
      state: STATE_ID,
      municipality: MUNICIPALITY_ID,
      locality: LOCALITY_ID,
    })
    const close_position = useClosePosition(full_main)
    expect(close_position.value).toEqual(LOCALITY)
    expect(close_position.value.municipality).toBe(MUNICIPALITY_ID)
  })

  it('cae a la cabecera del municipio cuando no hay localidad', () => {
    const full_main = ref({
      state: STATE_ID,
      municipality: MUNICIPALITY_ID,
      locality: null,
    })
    const close_position = useClosePosition(full_main)
    expect(close_position.value).toEqual(MUNICIPALITY)
    expect(close_position.value.state).toBe(STATE_ID)
  })

  it('devuelve null cuando no hay municipio', () => {
    const full_main = ref({state: STATE_ID, municipality: null, locality: null})
    expect(useClosePosition(full_main).value).toBeNull()
  })
})
