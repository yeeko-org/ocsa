<script setup>

import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";

const props = defineProps({
  final_filters: Object,
  field: String,
  label: String,
})

const lte = computed(() => {
  return props.field + '__lte'
})
const gte = computed(() => {
  return props.field + '__gte'
})

</script>

<template>
  <SelectDate
    :init_date="final_filters[gte]"
    label="Desde"
    class="mr-2"
    @update-date="final_filters[gte] = $event"
    is_filter
    max_width="130px"
    min-width="100px"
  />
  <SelectDate
    :init_date="final_filters[lte]"
    label="Hasta"
    class="mr-2"
    @update-date="final_filters[lte] = $event"
    is_filter
    max_width="130px"
    min-width="100px"
  />
</template>

<style scoped>

</style>