<script setup>

import { computed } from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  group: Object,
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
    :group="group"
  >
  </HeaderCommon>

</template>

<style scoped>

</style>