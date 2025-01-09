<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})
</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon>
      <SelectGroup
        :main_object="main"
        filter_group_name="impact_types"
        main_collection_name="impact"
        field="impact_type"
        forced_level="subtype"
        is_display
      />
    </template>
    <template #title>
      <div
        class="ml-2 font-weight-bold"
        style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
        v-tooltip:bottom="main.description"
      >{{ main.description }}</div>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>