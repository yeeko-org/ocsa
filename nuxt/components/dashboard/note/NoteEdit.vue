<script setup lang="ts">

import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
const props = defineProps({
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})
</script>

<template>
<v-card-text class="d-flex flex-wrap">
  <v-text-field
    v-model="full_main.title"
    label="Título de la nota"
    variant="outlined"
    style="width: 100%;"
  >
  </v-text-field>
  <GenericSelect
    :final_filters="full_main"
    collection="sources"
    field="source"
    label="Medio o fuente"
    clearable
    hide_details
    style="width: 200px;"
    class="mr-2"
    density="default"
  />
  <v-text-field
    v-model="full_main.section"
    label="Sección"
    variant="outlined"
    class="mr-2"
    style="width: 200px;"
  >
  </v-text-field>
  <v-text-field
    v-model="full_main.link"
    label="Enlace a la nota"
    variant="outlined"
    class="mr-2"
    style="width: 600px;"
  >
  </v-text-field>
  <StatusDetail
    :final_filters="full_main"
    field="status_register"
    collection="register"
    label="Status de registro"
    style="max-width: 300px;"
    density="default"
  />
</v-card-text>
</template>

<style scoped>

</style>