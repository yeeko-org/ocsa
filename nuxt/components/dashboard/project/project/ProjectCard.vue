<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

const props = defineProps({
  full_main: Object,
})

</script>

<template>
  <div class="py-2">
    <div class="d-flex align-center">
      <v-icon
        v-if="full_main.is_grouper"
        class="mr-2"
        v-tooltip="'Es un agrupador de proyectos.'"
      >
        group_work
      </v-icon>
      <div class="text-h6">
        {{ full_main.name }}
      </div>
    </div>
    <div class="d-flex flex-wrap">
      <StatusChip
        v-if="full_main.status_validation"
        :main="full_main"
        collection="validation"
        class="mb-1"
        bold_text
        x_small
      />
      <ExtractivismIcons
        :project="full_main"
        show_name
        class="ml-2"
      />
    </div>
  </div>
</template>

<style scoped>

</style>