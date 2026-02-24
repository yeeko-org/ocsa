<script setup>

import ImpactSheet from "~/components/dashboard/impact/impact/ImpactSheet.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
  collection_data: Object,
})

</script>

<template>
  <ImpactSheet
    :full_main="full_main"
  />
</template>

<style scoped>

</style>