<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})

</script>

<template>
  <SelectGroup
    filter_group_name="sectors"
    :main_object="full_main"
    main_collection_name="sector"
    :width="360"
    forced_level="subtype"
  />
</template>

<style scoped>

</style>