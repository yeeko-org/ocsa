<script setup>

import { computed } from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const project = computed(() => {
  return props.main
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