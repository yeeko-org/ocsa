export function useRules() {
  const rules = {
    required: (v) => !!v || 'Este campo es requerido',
    some_in_array: (v) => (Array.isArray(v) && v.length > 0) || 'Selecciona al menos una opción',
    required_adaptative: (v) => {
      if (Array.isArray(v)) {
        return v.length > 0 || 'Selecciona al menos una opción'
      }
      return !!v || 'Este campo es requerido'
    }
  }

  return {
    rules,
  }
}