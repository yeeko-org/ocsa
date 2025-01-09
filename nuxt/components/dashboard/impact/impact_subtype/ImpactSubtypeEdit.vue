<script setup >

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

</script>

<template>
  <SelectGroup
    filter_group_name="impact_types"
    :main_object="full_main"
    forced_level="subtype"
  />

</template>

<style scoped>

</style>