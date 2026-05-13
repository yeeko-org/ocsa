import { useMainStore } from "~/store/index.js"

export function useDeleteWithReport() {
  const report_data = ref(null)
  const deleting = ref(false)
  const delete_errors = ref(null)

  function reset() {
    report_data.value = null
    delete_errors.value = null
    deleting.value = false
  }

  async function tryDelete(snake_name, id) {
    const { deleteSimple } = useMainStore()
    deleting.value = true
    delete_errors.value = null
    const res = await deleteSimple([snake_name, id])
    deleting.value = false
    if (res.report_data) {
      report_data.value = res.report_data
      return { needs_confirmation: true }
    }
    if (res.errors) {
      delete_errors.value = res.errors
      return { error: true }
    }
    return { success: true }
  }

  async function confirmForceDelete(snake_name, id) {
    const { confirmDeleteSimple } = useMainStore()
    deleting.value = true
    delete_errors.value = null
    const res = await confirmDeleteSimple([snake_name, id])
    deleting.value = false
    if (res.errors) {
      delete_errors.value = res.errors
      return { error: true }
    }
    return { success: true }
  }

  return {
    report_data,
    deleting,
    delete_errors,
    tryDelete,
    confirmForceDelete,
    reset,
  }
}