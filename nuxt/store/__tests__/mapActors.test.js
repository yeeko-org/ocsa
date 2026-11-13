import {describe, expect, it, beforeEach} from 'vitest'
import {createPinia, setActivePinia} from 'pinia'
import {useMainStore} from '~/store/index.js'
import {useMapStore} from '~/store/map.js'

const FAVOR = 1
const CONTRA = 2
const NEUTRAL = 3

// Forma real de `/map/actors/`: actor_projects anidado por par
// {actorId: {projectId: [positionIds]}}, keyed por string en los dos niveles.
// El proyecto 12 es el caso que motiva el par: el actor 1 es neutral y el
// actor 2 está en contra. El 11 es una participación sin tipo (lista vacía).
const PAYLOAD = {
  actors: [
    {id: 1, name: 'Frente Wixárika'},
    {id: 2, name: 'Frente Minero'},
    {id: 3, name: 'Frente Agrario'},
  ],
  positions: [
    {id: FAVOR, name: 'A favor'},
    {id: CONTRA, name: 'En contra'},
    {id: NEUTRAL, name: 'Neutral'},
  ],
  actor_projects: {
    '1': {'10': [CONTRA], '11': [], '12': [NEUTRAL]},
    '2': {'12': [CONTRA], '13': [FAVOR]},
    '3': {'13': [FAVOR]},
  },
}

const ids = set => [...set].sort((a, b) => a - b)

// El store real, con el payload ya en el main store: `fetchMapActors` hace
// early return si `mapActors` existe, así que no hay red que simular.
async function loadedStore() {
  useMainStore().mapActors = structuredClone(PAYLOAD)
  const store = useMapStore()
  await store.ensureActors()
  return store
}

describe('filtro de actores del mapa', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('carga el payload anidado de actor_projects sin lanzar', async () => {
    useMainStore().mapActors = structuredClone(PAYLOAD)
    const store = useMapStore()
    await expect(store.ensureActors()).resolves.toBeUndefined()
    expect(store.actorsReady).toBe(true)
  })

  it('un actor solo deja los proyectos de ese actor', async () => {
    const store = await loadedStore()
    store.filters.actors = [{id: 1, name: 'Frente Wixárika'}]
    expect(ids(store.visibleProjectIds)).toEqual([10, 11, 12])
  })

  it('actor + posición se evalúan por par, no por intersección', async () => {
    const store = await loadedStore()
    store.filters.actors = [{id: 1, name: 'Frente Wixárika'}]
    store.filters.positions = [CONTRA]
    // El 12 queda fuera: ahí el actor 1 es neutral; quien está en contra es
    // el actor 2.
    expect(ids(store.visibleProjectIds)).toEqual([10])
  })

  it('una posición sola deja los proyectos donde algún actor la tiene',
    async () => {
      const store = await loadedStore()
      store.filters.positions = [CONTRA]
      expect(ids(store.visibleProjectIds)).toEqual([10, 12])
    })

  it('un par sin posiciones cuenta para el actor pero nunca para una posición',
    async () => {
      const store = await loadedStore()
      store.filters.actors = [{id: 1, name: 'Frente Wixárika'}]
      expect(store.visibleProjectIds.has(11)).toBe(true)
      store.filters.positions = [FAVOR, CONTRA, NEUTRAL]
      expect(store.visibleProjectIds.has(11)).toBe(false)
      store.filters.actors = []
      expect(store.visibleProjectIds.has(11)).toBe(false)
    })

  it('con posiciones activas el buscador solo ofrece actores que las tienen',
    async () => {
      const store = await loadedStore()
      const selected = [{id: 1, name: 'Frente Wixárika'}]
      store.filters.actors = selected
      expect(ids(store.searchActors('frente').map(a => a.id)))
        .toEqual([1, 2, 3])
      store.filters.positions = [FAVOR]
      expect(ids(store.searchActors('frente').map(a => a.id)))
        .toEqual([2, 3])
      expect(store.filters.actors).toEqual(selected)
    })
})
