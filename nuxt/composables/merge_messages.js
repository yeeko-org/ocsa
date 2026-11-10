// generic_merge/ answers in several shapes: `{errors: [...]}` from the
// merger, DRF serializer dicts, a bare list from a ValidationError, and
// `{detail}` from the permission check.
function flatten(value) {
  if (value === null || value === undefined) return []
  // A 500 page from Django or nginx is HTML, not a message for the editor.
  if (typeof value === 'string')
    return value.trim() && !value.trim().startsWith('<') ? [value] : []
  if (Array.isArray(value)) return value.flatMap(flatten)
  if (typeof value === 'object') {
    if (value.detail)
      return [value.reason
        ? `${value.detail}: ${value.reason}` : value.detail]
    if (value.errors) return flatten(value.errors)
    return Object.values(value).flatMap(flatten)
  }
  return [String(value)]
}

const fallback_by_status = {
  400: 'Este tipo de registro no se puede fusionar.',
  403: 'No tienes permiso para fusionar estos registros.',
}

export function mergeErrorText(error_data, status) {
  const server_msgs = flatten(error_data)
  if (server_msgs.length) return server_msgs.join(' ')
  if (!status) return 'No hubo respuesta del servidor.'
  return fallback_by_status[status]
    || `El servidor no pudo completar la fusión (error ${status}).`
}

function listLabels(labels) {
  return labels.map(label => `«${label}»`).join(', ')
}

export function mergeFailureText(
    {main_label, merged, failed, reason, pending}) {
  const parts = []
  if (merged.length)
    parts.push(`Se fusionaron en «${main_label}»: ${listLabels(merged)}.`)
  else
    parts.push('No se fusionó ningún registro.')
  parts.push(`Falló «${failed}»: ${reason}`)
  if (pending.length)
    parts.push(`Quedaron sin fusionar: ${listLabels(pending)}.`)
  return parts.join(' ')
}

export function mergeSuccessText(main_label, count) {
  return count === 1
    ? `Se fusionó 1 registro en «${main_label}»`
    : `Se fusionaron ${count} registros en «${main_label}»`
}
