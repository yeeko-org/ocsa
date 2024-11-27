<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

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
  </HeaderCommon>
</template>

<style scoped>

</style>
