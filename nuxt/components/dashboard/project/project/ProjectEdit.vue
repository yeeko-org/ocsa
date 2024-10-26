<script setup>

import MegaProjectType from "~/components/dashboard/project/MegaProjectType.vue";
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
  <v-card-text>

    <div class="d-flex">
      <v-text-field
        v-model="full_main.official_name"
        label="Nombre oficial"
        width="400"
        max-width="400"
        variant="outlined"
      >
      </v-text-field>
      <StatusDetail
        :final_filters="full_main"
        field="status_register"
        collection="register"
        label="Status de registro"
        style="max-width: 300px;"
      />
    </div>
    <MegaProjectType
      :project="full_main"
    />
  </v-card-text>
</template>

<style scoped>

</style>