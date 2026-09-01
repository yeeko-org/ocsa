import {computed, unref} from 'vue'
import {storeToRefs} from 'pinia'
import {useMainStore} from '~/store'
import {useAuthStore} from '~/store/auth.js'

// Lo que se muestra cuando el registro trae un status que ya no está en el
// catálogo: preferimos un chip gris legible a no pintar nada.
export const UNDEFINED_STATUS = {
  public_name: 'Sin definir',
  color: 'grey',
  color_text: 'white',
  icon: 'help',
  back_text: 'text-grey-darken-1',
}

export function groupKeyOf(source) {
  if (!source) return null
  if (typeof source === 'string')
    return source.replace(/^status_/, '')
  return source.key_name || null
}

/**
 * Decide si el status puede editarse y cuáles pueden asignarse.
 *
 * Pura a propósito: es la única definición de la escalera de permisos
 * del front y se prueba sin store ni componentes.
 */
export function statusPolicy(
  {user_flags = {}, selected = null, is_filter = false, readonly = false}) {
  const {is_superuser = false, is_full_editor = false} = user_flags

  const is_readonly = (() => {
    if (is_filter) return false
    if (readonly) return true
    if (is_superuser) return false
    // Sin status no hay candado; tener uno legacy tampoco cierra el campo
    // (task-71: se ve siempre, solo no se asigna).
    return selected?.open_editor === false
  })()

  const isSelectable = (status) => {
    if (is_filter) return true
    if (readonly) return false
    if (!status) return false
    if (status.is_legacy) return is_superuser
    if (is_superuser || is_full_editor) return true
    return !!status.open_selectable
  }

  return {is_readonly, isSelectable}
}

/**
 * Resuelve un grupo de status desde un objeto ya enriquecido o desde su
 * nombre en cualquiera de los dos vocabularios (`location` /
 * `status_location`), al modo de `DisplayGroup`.
 */
export function useStatusGroup(source, options = {}) {
  const {record = null, is_filter = null, readonly = null} = options
  const main_store = useMainStore()
  const auth_store = useAuthStore()
  const {status, status_dict, status_groups_dict} = storeToRefs(main_store)
  const {is_full_editor, is_superuser} = storeToRefs(auth_store)

  const group = computed(() => {
    const raw = unref(source)
    if (raw && typeof raw === 'object' && raw.field_name)
      return raw
    const key = groupKeyOf(raw)
    return key ? status_groups_dict.value[key] || null : null
  })

  const key_name = computed(() => group.value?.key_name || null)
  const field = computed(() => group.value?.field_name || null)
  const label = computed(() =>
    group.value ? `Status de ${group.value.public_name}` : '')
  const short_label = computed(() =>
    group.value ? `${group.value.public_name}:` : '')

  const items = computed(() =>
    key_name.value ? status.value[key_name.value] || [] : [])
  const items_dict = computed(() =>
    key_name.value ? status_dict.value[key_name.value] || {} : {})

  const status_name = computed(() => {
    const main = unref(record)
    if (!main || !field.value) return null
    return main[field.value] || null
  })

  // `selected` es null cuando no hay status: la política lo lee como
  // abierto y la vista pinta `fallback`, que son dos cosas distintas.
  const selected = computed(() =>
    status_name.value ? items_dict.value[status_name.value] || null : null)

  const fallback = computed(() => UNDEFINED_STATUS)

  const display = computed(() =>
    selected.value || (status_name.value ? UNDEFINED_STATUS : null))

  const policy = computed(() => statusPolicy({
    user_flags: {
      is_superuser: is_superuser.value,
      is_full_editor: is_full_editor.value,
    },
    selected: selected.value,
    is_filter: unref(is_filter) || false,
    readonly: unref(readonly) || false,
  }))

  const is_readonly = computed(() => policy.value.is_readonly)
  const isSelectable = (item) => policy.value.isSelectable(item)

  return {
    group, key_name, field, label, short_label,
    items, items_dict, selected, display, fallback,
    is_readonly, isSelectable,
  }
}
