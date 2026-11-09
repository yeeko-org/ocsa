import {describe, expect, it} from 'vitest'
import {matchesSearch} from '~/composables/selectSearch.js'

const WIXARIKA = {id: 1, name: 'Wixárika', alternative_names: 'Huichol'}
const MIXTECO = {id: 2, name: 'Mixteco', alternative_names: 'Ñuu Savi'}
const PUREPECHA = {
  id: 3, name: 'Otro', description: 'Comunidad purépecha de Cherán'}

describe('matchesSearch', () => {
  it('ignora los acentos de la consulta y del nombre', () => {
    expect(matchesSearch(WIXARIKA, 'wixarika')).toBe(true)
    expect(matchesSearch(WIXARIKA, 'WIXÁRIKA')).toBe(true)
    expect(matchesSearch({name: 'Wixarika'}, 'wixárika')).toBe(true)
  })

  it('ignora los apóstrofos rectos y tipográficos', () => {
    const MEPHAA = {name: 'Me´phaa (Tlapaneco)', alternative_names: "Ch’ol"}
    expect(matchesSearch(MEPHAA, 'mephaa')).toBe(true)
    expect(matchesSearch(MEPHAA, "me'phaa")).toBe(true)
    expect(matchesSearch(MEPHAA, 'meʾphaa')).toBe(true)
    expect(matchesSearch(MEPHAA, "ch'ol")).toBe(true)
    expect(matchesSearch(MEPHAA, 'chol')).toBe(true)
  })

  it('pliega la ñ y busca en los nombres alternativos', () => {
    expect(matchesSearch(MIXTECO, 'nuu savi')).toBe(true)
    expect(matchesSearch(WIXARIKA, 'huichol')).toBe(true)
  })

  it('busca sin acentos en la descripción', () => {
    expect(matchesSearch(PUREPECHA, 'purepecha')).toBe(true)
  })

  it('no confunde lo que no coincide y acepta la consulta vacía', () => {
    expect(matchesSearch(WIXARIKA, 'mixteco')).toBe(false)
    expect(matchesSearch(WIXARIKA, '')).toBe(true)
  })

  it('respeta item_title', () => {
    expect(matchesSearch({short_name: 'Purépecha'}, 'purepecha',
      'short_name')).toBe(true)
  })
})
