<script setup>

import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";

const props = defineProps({
  final_filters: Object,
  field: String,
  label: String,
})

</script>

<template>
  <SelectDate
    :init_date="final_filters.start_date"
    label="Desde"
    class="mr-2"
    @update-date="final_filters.start_date = $event"
    is_filter
    max_width="130px"
  />
  <SelectDate
    :init_date="final_filters.end_date"
    label="Hasta"
    class="mr-2"
    @update-date="final_filters.end_date = $event"
    is_filter
    max_width="130px"
  />

</template>

<style scoped>

</style>