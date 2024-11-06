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