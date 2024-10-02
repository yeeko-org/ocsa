<script setup>

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
  <v-row>
    <v-col cols="auto">
      <v-text-field
        v-model="full_main.name"
        label="Nombre del tipo de megaproyecto"
        width="360"
        variant="outlined"
      >
      </v-text-field>
    </v-col>
    <v-col>
      <v-text-field
        v-model="full_main.order"
        label="Orden"
        type="number"
        width="100"
        variant="outlined"
      >
      </v-text-field>
    </v-col>
    <v-col>
      <GenericSelect
        :final_filters="full_main"
        field="extractivism_types"
        collection="extractivism_types"
        label="Tipos de extractivismo"
        :clearable="false"
        density="default"
        width="260"
        multiple
      />
    </v-col>
    <v-col>
      <StatusDetail
        :final_filters="full_main"
        field="status_validation"
        collection="validation"
        label="Status de validación"
        _style="max-width: 300px;"
        width="300"
        :clearable="false"
      />
    </v-col>
    <v-col cols="12">
      <v-textarea
        v-model="full_main.description"
        label="Descripción de la categoría"
        variant="outlined"
        rows="3"
        max-rows="5"
      >
      </v-textarea>
    </v-col>
  </v-row>
</template>

<style scoped>

</style>