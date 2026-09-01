import {describe, expect, it, beforeEach} from 'vitest'
import {ref} from 'vue'
import {createPinia, setActivePinia} from 'pinia'
import {useMainStore} from '~/store'
import {useAuthStore} from '~/store/auth.js'
import {
  useStatusGroup, statusPolicy, groupKeyOf, UNDEFINED_STATUS,
} from '~/composables/useStatusGroup.js'

const GROUPS = [
  {key_name: 'validation', public_name: 'Validación', order: 5,
    hidden: false},
  {key_name: 'location', public_name: 'Ubicación', order: 6,
    hidden: false},
]

// `open_editor` y `open_selectable` son el discriminante de la escalera:
// cambiarlos aquí invalida las aserciones de política de abajo.
const APPROVED = {
  name: 'finished', public_name: 'Aprobado', open_editor: false,
  open_selectable: false, is_legacy: false,
}
const DRAFT = {
  name: 'initial', public_name: 'Datos iniciales', open_editor: true,
  open_selectable: true, is_legacy: false,
}
const LEGACY = {
  name: 'migrated_v1', public_name: 'v1. Migrado', open_editor: true,
  open_selectable: true, is_legacy: true,
}

function fillStore({full_editor = false, superuser = false} = {}) {
  const main = useMainStore()
  main.cats = {status_group: GROUPS, status_control: []}
  main.status = {location: [APPROVED, DRAFT, LEGACY], validation: []}
  const auth = useAuthStore()
  auth.user_details_ocsa = {
    is_full_editor: full_editor, is_staff: false, is_superuser: superuser,
  }
}

describe('statusPolicy', () => {
  const editor = {is_full_editor: true, is_superuser: false}
  const plain = {is_full_editor: false, is_superuser: false}
  const boss = {is_full_editor: false, is_superuser: true}

  it('como filtro nunca bloquea ni deshabilita opciones', () => {
    const p = statusPolicy({
      user_flags: plain, selected: APPROVED, is_filter: true})
    expect(p.is_readonly).toBe(false)
    expect(p.isSelectable(APPROVED)).toBe(true)
    expect(p.isSelectable(LEGACY)).toBe(true)
  })

  it('el readonly del schema gana sobre cualquier rol', () => {
    const p = statusPolicy({
      user_flags: boss, selected: DRAFT, readonly: true})
    expect(p.is_readonly).toBe(true)
    expect(p.isSelectable(DRAFT)).toBe(false)
  })

  it('un status cerrado bloquea al editor pleno, no al superusuario', () => {
    expect(statusPolicy({user_flags: editor, selected: APPROVED})
      .is_readonly).toBe(true)
    expect(statusPolicy({user_flags: boss, selected: APPROVED})
      .is_readonly).toBe(false)
  })

  it('un status abierto no bloquea a nadie', () => {
    expect(statusPolicy({user_flags: plain, selected: DRAFT})
      .is_readonly).toBe(false)
  })

  it('sin status el campo se edita', () => {
    expect(statusPolicy({user_flags: plain, selected: null})
      .is_readonly).toBe(false)
  })

  it('tener un status legacy no cierra el campo', () => {
    expect(statusPolicy({user_flags: plain, selected: LEGACY})
      .is_readonly).toBe(false)
  })

  it('el legacy solo lo asigna el superusuario', () => {
    expect(statusPolicy({user_flags: plain}).isSelectable(LEGACY))
      .toBe(false)
    expect(statusPolicy({user_flags: editor}).isSelectable(LEGACY))
      .toBe(false)
    expect(statusPolicy({user_flags: boss}).isSelectable(LEGACY))
      .toBe(true)
  })

  it('open_selectable solo limita a quien no es editor pleno', () => {
    expect(statusPolicy({user_flags: plain}).isSelectable(APPROVED))
      .toBe(false)
    expect(statusPolicy({user_flags: editor}).isSelectable(APPROVED))
      .toBe(true)
    expect(statusPolicy({user_flags: plain}).isSelectable(DRAFT))
      .toBe(true)
  })
})

describe('groupKeyOf', () => {
  it('normaliza los dos vocabularios y el objeto', () => {
    expect(groupKeyOf('location')).toBe('location')
    expect(groupKeyOf('status_location')).toBe('location')
    expect(groupKeyOf({key_name: 'location'})).toBe('location')
    expect(groupKeyOf(null)).toBe(null)
  })
})

describe('useStatusGroup', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fillStore()
  })

  it('resuelve desde el nombre corto', () => {
    const {group, field, key_name} = useStatusGroup('location')
    expect(key_name.value).toBe('location')
    expect(field.value).toBe('status_location')
    expect(group.value.public_name).toBe('Ubicación')
  })

  it('resuelve desde el nombre del campo', () => {
    const {field, label} = useStatusGroup('status_location')
    expect(field.value).toBe('status_location')
    expect(label.value).toBe('Status de Ubicación')
  })

  it('acepta el objeto enriquecido sin consultar el store', () => {
    const enriched = {
      ...GROUPS[1], field_name: 'status_location', name: 'status_location'}
    const {group, short_label} = useStatusGroup(enriched)
    expect(group.value).toBe(enriched)
    expect(short_label.value).toBe('Ubicación:')
  })

  it('sigue una fuente reactiva', () => {
    const source = ref('validation')
    const {field} = useStatusGroup(source)
    expect(field.value).toBe('status_validation')
    source.value = 'status_location'
    expect(field.value).toBe('status_location')
  })

  it('no revienta con un grupo inexistente', () => {
    const {group, field, items, label} = useStatusGroup('inventado')
    expect(group.value).toBe(null)
    expect(field.value).toBe(null)
    expect(items.value).toEqual([])
    expect(label.value).toBe('')
  })

  it('resuelve el status del registro y su política', () => {
    const record = ref({status_location: 'finished'})
    const {selected, is_readonly} = useStatusGroup('location', {record})
    expect(selected.value.public_name).toBe('Aprobado')
    expect(is_readonly.value).toBe(true)
  })

  it('un registro sin status es editable y no pinta chip', () => {
    const record = ref({})
    const {selected, display, is_readonly} =
      useStatusGroup('location', {record})
    expect(selected.value).toBe(null)
    expect(display.value).toBe(null)
    expect(is_readonly.value).toBe(false)
  })

  it('un status fuera del catálogo cae en «Sin definir»', () => {
    const record = ref({status_location: 'fantasma'})
    const {selected, display} = useStatusGroup('location', {record})
    expect(selected.value).toBe(null)
    expect(display.value).toBe(UNDEFINED_STATUS)
  })

  it('como filtro no bloquea aunque el status esté cerrado', () => {
    const record = ref({status_location: 'finished'})
    const {is_readonly} = useStatusGroup(
      'location', {record, is_filter: true})
    expect(is_readonly.value).toBe(false)
  })

  it('lee los flags del usuario desde el store', () => {
    fillStore({superuser: true})
    const record = ref({status_location: 'finished'})
    const {is_readonly, isSelectable} =
      useStatusGroup('location', {record})
    expect(is_readonly.value).toBe(false)
    expect(isSelectable(LEGACY)).toBe(true)
  })
})
