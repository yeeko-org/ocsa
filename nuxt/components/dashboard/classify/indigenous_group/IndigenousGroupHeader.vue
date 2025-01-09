<script setup>
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

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
    <template #details>
      <HeaderChip
        class="ml-3"
        :count="main.count"
        collection_name="actor"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>