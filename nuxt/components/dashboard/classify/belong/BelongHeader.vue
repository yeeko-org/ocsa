<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

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