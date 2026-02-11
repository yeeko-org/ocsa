<script setup>

import TripleBooleanFilter from "~/components/dashboard/custom_filters/TripleBooleanFilter.vue";

const props = defineProps({
  final_filters: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <TripleBooleanFilter
    :final_filters="final_filters"
    field="has_conflict"
    label="Tiene conflicto"
    class="pr-3 pl-0 py-1"
    max-width="180"
  />
  <TripleBooleanFilter
    :final_filters="final_filters"
    field="conflict_criteria"
    label="Cumple los criterios"
    class="pr-3 pl-0 py-1"
    max-width="200"
  />
</template>

<style scoped>

</style>