<script setup>

defineProps({
  import_warnings: {
    type: Array,
    default: () => [],
  },
  // Ayudas del tipo de ubicación; sólo llegan con el mapa abierto
  helps: {
    type: Array,
    default: null,
  },
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
    La importación reemplazó la geometría guardada; al guardar se perderá
    la información anterior.
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
