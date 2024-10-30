<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import {useMainStore} from '~/store/index.js'
import {storeToRefs} from 'pinia'
const mainStore = useMainStore()
const { groups } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  mentions: Array,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})


</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #details>
      holi
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>