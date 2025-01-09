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
    :main_object="full_main"
    filter_group_name="event_types"
    main_collection_name="event_subtype"
    field="event_types"
    forced_level="subtype"
    required
  />
</template>

<style scoped>

</style>