<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";

const props = defineProps({
  full_main: Object,
})

</script>

<template>
  <div class="py-2">
    <div class="text-h6">
      {{ full_main.name }}
    </div>
    <div class="d-flex flex-wrap">
      <StatusChip
        v-if="full_main.status_validation"
        :main="full_main"
        collection="validation"
        class="mb-1"
        only_icon
        x_small
        hide_details
      />
    </div>
  </div>
</template>

<style scoped>

</style>