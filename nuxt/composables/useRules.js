export function useRules() {
  const rules = {
    required: (v) => !!v || 'Este campo es requerido',
  }

  return {
    rules,
  }
}