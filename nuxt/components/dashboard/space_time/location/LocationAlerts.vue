<script setup>

const props = defineProps({
  import_warnings: {
    type: Array,
    default: () => [],
  },
  // Ayudas del tipo de ubicación; sólo llegan con el mapa abierto
  helps: {
    type: Array,
    default: null,
  },
  geo_notices: {
    type: Array,
    default: () => [],
  },
  nearby_localities: {
    type: Number,
    default: null,
  },
  type_location: {
    type: String,
    default: null,
  },
})

// Cerrar un aviso no puede tocar el arreglo del padre, que es su dueño
const dismissed = ref([])

watch(() => props.geo_notices, () => dismissed.value = [])

const visible_notices = computed(
    () => props.geo_notices.filter(msg => !dismissed.value.includes(msg)))

const localities_notice = computed(() => {
  if (props.type_location === 'point') return null
  if (props.nearby_localities === null) return null
  if (props.nearby_localities === 0)
    return 'El trazo no toca ni pasa cerca de ninguna localidad; '
        + 'el campo Localidad queda vacío.'
  if (props.nearby_localities > 1)
    return `El trazo toca o pasa cerca de ${props.nearby_localities} `
        + 'localidades: por eso el campo Localidad queda vacío. '
        + 'Puedes elegir una a mano si corresponde.'
  return null
})

const import_error = defineModel('import_error', {type: String, default: ''})
const overwrote_saved = defineModel(
    'overwrote_saved', {type: Boolean, default: false})

</script>

<template>
  <v-alert
    v-if="import_error"
    type="error"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="import_error = ''"
  >
    {{ import_error }}
  </v-alert>
  <v-alert
    v-if="overwrote_saved"
    type="warning"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="overwrote_saved = false"
  >
    El archivo que importaste reemplazó lo que estaba marcado en el mapa;
    si guardas, se pierde lo anterior.
  </v-alert>
  <v-alert
    v-for="msg in import_warnings"
    :key="msg"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
  >
    {{ msg }}
  </v-alert>
  <v-alert
    v-for="msg in visible_notices"
    :key="msg"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
    closable
    @click:close="dismissed.push(msg)"
  >
    {{ msg }}
  </v-alert>
  <v-alert
    v-if="localities_notice"
    type="info"
    variant="tonal"
    class="mb-2"
    density="compact"
  >
    {{ localities_notice }}
  </v-alert>
  <v-alert
    v-if="helps"
    type="info"
    variant="tonal"
    class="mt-3"
    density="compact"
  >
    <div
      v-for="msg in helps"
      :key="msg"
    >
      {{ msg }}
    </div>
  </v-alert>
</template>
