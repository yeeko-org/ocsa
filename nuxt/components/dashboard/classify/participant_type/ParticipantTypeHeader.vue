<script setup>

import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/utils/HeaderChip.vue";
import DisplayGroup from "~/components/dashboard/common/select/DisplayGroup.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>

  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon>
      <DisplayGroup
        filter_group_name="participant_types"
        :main_object="main"
        main_collection_name="participan_type"
        forced_level="subtype"
      />
    </template>
    <template #details>
      <HeaderChip
        :count="main.actors_count"
        collection_name="actor"
        class="ml-2"
        horizontal
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>